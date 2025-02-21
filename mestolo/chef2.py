from typing import Optional
import uuid
import multiprocessing as mp
import signal
import math
import time
from queue import Empty, PriorityQueue
from datetime import datetime

from sqlalchemy.orm import Session
from croniter import croniter

from mestolo.recipe import Menu

class Chef:
    def __init__(self, menu: Menu,
                 num_cooks: int,
                 session: Optional[Session] = None,
                 duration: float =   math.inf,
                 refresh_rate: float = 1.0):
        now = datetime.now()
        self.session = session or Session()

        self._num_cooks = num_cooks
        self._menu = menu
        self._duration = duration
        self._refresh_rate = refresh_rate

        self._processes = []
        self._croniters = {recipe.name: croniter(recipe.schedule, now)
                           for recipe in self._menu.recipes.values() if recipe.schedule is not None}

        self._schedule = PriorityQueue()

    def _cook_recipe(self, recipe_id: uuid.UUID):
        recipe = self._menu[recipe_id]

        # TODO: update database

        p = mp.Process(target=recipe.cook)  # do we need queue args?
        self._processes.append(p)
        p.start()

    def _clean_processes(self):
        self._processes = [p for p in self._processes if p.is_alive()]
        return len(self._processes)

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
                self._cook_scheduled_item(self._schedule.get())
                free_cook_count -= 1

            # run the monitoring update

            # TODO: actually do the cooking!

            loop_duration = time.time() - loop_start_time
            time.sleep(max(self._refresh_rate - loop_duration, 0))

    def close(self):
        for p in self._processes:
            p.join()


