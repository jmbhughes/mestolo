from collections import namedtuple
from typing import Callable
import time
from prefect import flow
from queue import PriorityQueue
from enum import Enum
import multiprocessing as mp
import signal
import math

IngredientInstance = namedtuple("IngredientInstance", ["ingredient_code", "reference_time", "version", "object"])

class CronSchedule:
    def __init__(self, cronstring: str) -> None:
        self._s = cronstring

def flatten_list[T](compound_list: list[list[T]]) -> list[T]:
    flat_list = []
    for entry in compound_list:
        flat_list += entry
    return flat_list

#TODO: make a recipe decorator

class TriggerType(Enum):
    AVAIBLILITY = 1
    SCHEDULE = 2
    MANUAL = 3

class Recipe:
    def __init__(self,
        name: str,
        input_ingredients: list[str],
        output_ingredients: list[str],
        function: Callable
    ):
        self._name = name
        self._inputs = input_ingredients
        self._outputs = output_ingredients
        self._f = function

    @property
    def inputs(self) -> list[str]:
        return self._inputs

    @property
    def outputs(self) -> list[str]:
        return self._outputs

    @property
    def name(self) -> str:
        return self._name

    @property
    def f(self) -> Callable:
        return self._f

    def cook(self, inputs: list[IngredientInstance]) -> list[IngredientInstance]:
        # TODO : validate inputs
        # TODO: validate outputs
        # TODO: pass things around properly
        return self._f(self._name)

class Menu:
    def __init__(self,
        recipes: list[Recipe],
        trigger_types: dict[Recipe, TriggerType],
        schedules: dict[Recipe, CronSchedule]):
        self._recipes = recipes
        self._trigger_types = trigger_types
        self._schedules = schedules

    @property
    def all_ingredients(self) -> list[str]:
        return flatten_list([r.inputs + r.outputs for r in self._recipes])

    @property
    def source_ingredients(self) -> list[str]:
        all_ingredients = set(self.all_ingredients)
        outputs = set(flatten_list([r.outputs for r in self._recipes]))
        return list(all_ingredients - outputs)

    @property
    def terminal_ingredients(self) -> list[str]:
        all_ingredients = set(self.all_ingredients)
        inputs = set(flatten_list([r.inputs for r in self._recipes]))
        return list(all_ingredients - inputs)

    @property
    def intermediate_ingredients(self) -> list[str]:
        return list(set(self.all_ingredients) - set(self.source_ingredients) - set(self.terminal_ingredients))

    def get_recipe_for(self, ingredient: str) -> list[Recipe]:
        return [r for r in self._recipes if ingredient in r.outputs]

class Chef:
    def __init__(self, num_workers: int = -1, refresh_seconds: float = 60.0, duration : float = math.inf):
        if num_workers == -1:
            num_workers = mp.cpu_count()

        if num_workers <= 0:
            raise RuntimeError("Must have at least 1 worker.")

        self._num_workers = num_workers
        self._refresh_seconds = refresh_seconds
        self._duration = duration

        self._order_queue = PriorityQueue()

    def cook(self, menu: Menu):
        running = True

        def interrupt_handler(this_signal, frame):
            nonlocal running
            running = False

        signal.signal(signal.SIGINT, interrupt_handler)

        start = time.time()
        while running and time.time() - start < self._duration:
            loop_start_time = time.time()

            # active_cook_count = self._clean_processes()
            # free_cook_count = self._num_cooks - active_cook_count

            # while free_cook_count > 0 and not self._schedule.empty():
            #     self._cook_recipe(self._schedule.get())
            #     free_cook_count -= 1
            m._recipes[0].cook([])
            # run the monitoring update

            # TODO: actually do the cooking!

            loop_duration = time.time() - loop_start_time
            time.sleep(max(self._refresh_seconds - loop_duration, 0))

@flow
def empty_cooker(*args, **kwargs):
    print(f"Starting {args[0]}")

    time.sleep(3)

    print(f"Ending {args[0]}")
    return []

if __name__ == "__main__":
    recipes = []
    # for level in [0, 1]:
    #     for observatory in range(1, 5):
    #         ingredients.append(Ingredient(f"L{level}_CR{observatory}"))

    # for observatory in range(1, 5):
    #     ingredients.append(Ingredient(f"L0_DS{observatory}"))

    for observatory in range(1, 5):
        r = Recipe(f"L1_CR{observatory}", [f"L0_CR{observatory}", f"L1_DS{observatory}"], [f"L1_CR{observatory}"], empty_cooker)
        recipes.append(r)

    mosaic_r = Recipe(f"L2_clear", ["L1_CR1", "L1_CR2", "L1_CR3", "L1_CR4"], ["L2_CTM"], empty_cooker)
    recipes.append(mosaic_r)

    m = Menu(recipes, None, None)
    print(m._recipes)
    print(m.all_ingredients)
    print("source", m.source_ingredients)
    print("terminal", m.terminal_ingredients)
    print("intermediate", m.intermediate_ingredients)

    c = Chef()
    c.cook(m)
