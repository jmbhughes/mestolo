from __future__ import annotations

from pathlib import Path
from typing import Callable, Any, TypeVar, get_origin, get_args
import functools
import multiprocessing as mp
import signal
import time
import math
from datetime import datetime, timedelta
from queue import Empty, PriorityQueue

from ndcube import NDCube
import numpy as np

Apple = TypeVar("Apple")
Banana = TypeVar("Banana")
Pie = TypeVar("Pie")
Peel = TypeVar("Peel")
Order = TypeVar("Order")

class Ingredient[K]:
    def __init__(self, identifier: int, data: Any):
        # self.kind = K
        self.identifier = identifier
        self.data = data

    def kind_matches[T](self, other: Ingredient[T]):
        return get_args(self.__orig_class__) == get_args(other.__orig_class__)

class BaseSelector:
    def __init__(self, kind: str, f: Callable[[int, int], bool]):
        self.kind = kind
        self.f = f

class WaitSelector(BaseSelector):
    def __init__(self, kind: str, f: Callable[[int, int], bool]):
        super().__init__(kind, f)

class BestEffortSelector(BaseSelector):
    def __init__(self, kind: str, f: Callable[[int, int], bool], duration: timedelta):
        super().__init__(kind, f)
        self._duration = duration

class FailSelector(BaseSelector):
    def __init__(self, kind: str, f: Callable[[int, int], bool], duration: timedelta):
        super().__init__(kind, f)
        self._duration = duration

class CollectionSelector(BaseSelector):
    def __init__(self, kind: str, f: Callable[[int, int], bool], target_count: int):
        super().__init__(kind, f)
        self._target_count = target_count

def recipe(input_selectors: list[BaseSelector]):
    def decorator(function):
        # TODO: validate parameters by count
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            print("Using", input_selectors)
            # TODO update database it's being made
            result = function(*args, **kwargs)
            # print("Made", output_kinds)
            # TODO update database that it's ready
            return result
        return wrapper
    return decorator

@recipe(input_selectors=
        [WaitSelector("apple", lambda a, b: a==b),
         WaitSelector("banana", lambda a, b: a==b)])
def level1a(a: Ingredient[Apple], b: Ingredient[Banana]) -> tuple[Ingredient[Pie], Ingredient[Peel]]:
    return None, None

@recipe(input_selectors=[CollectionSelector("pie", lambda a, b: abs(a-b) < 30, 100)])
def level1b(a: list[Ingredient[Pie]]) -> Ingredient[Order]:
    return None

class Order:
    def __init__(self, recipe: Callable, inputs: list[Ingredient]):
        self.recipe = recipe
        self.inputs = inputs

class Chef:
    def __init__(self,
                 recipe_path: str | Path,
                 num_cooks: int,
                 duration: float = math.inf,
                 refresh_rate: float = 1.0):
        self._recipe_path = Path(recipe_path)
        # TODO: collect receipts and make graph

        self._start = datetime.now()

        self._num_cooks: int = num_cooks
        self._duration: float = duration
        self._refresh_rate: float = refresh_rate

        self._processes: list[mp.Process] = []
        self._schedule: PriorityQueue[Order] = PriorityQueue()


    def _clean_processes(self):
        self._processes = [p for p in self._processes if p.is_alive()]
        return len(self._processes)

    def _cook_order(self, order: Order):
        # TODO: update database
        p = mp.Process(target=order.recipe, args=order.inputs)
        self._processes.append(p)
        p.start()

    def schedule_order(self, order:Order):
        self._schedule.put(order)

    def cook(self):
        running = True

        def interrupt_handler(this_signal, frame):
            nonlocal running
            running = False

        signal.signal(signal.SIGINT, interrupt_handler)

        start = time.time()
        while running and time.time() - start < self._duration:
            loop_start_time = time.time()

            active_cook_count = self._clean_processes()
            free_cook_count = self._num_cooks - active_cook_count

            while free_cook_count > 0 and not self._schedule.empty():
                self._cook_order(self._schedule.get())
                free_cook_count -= 1

            # TODO run the monitoring update

            loop_duration = time.time() - loop_start_time
            time.sleep(max(self._refresh_rate - loop_duration, 0))

    def close(self):
        for p in self._processes:
            p.join()

if __name__ == "__main__":
    chef = Chef(recipe_path="bob.txt", num_cooks=10, duration=10)
    o1 = Order(level1a,
               [Ingredient[Apple]( 1, "A"),
                Ingredient[Banana]( 1, "B")])
    chef.schedule_order(o1)
    chef.cook()

# make the chef taken in a recipe file and generate the dependency graph
# make a sensor recipe
# make the chef schedule the outcomes of the recipe
# make some selectors
# make the chef handle the "fail" and "delay" selectors
