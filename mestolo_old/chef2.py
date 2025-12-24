from typing import Optional, List
import uuid
import multiprocessing as mp
import signal
import math
import time
from queue import Empty, PriorityQueue
from datetime import datetime, timedelta

import sqlalchemy as sa
from sqlalchemy.orm import Session
from croniter import croniter

from mestolo.db import create_session, RecipeDB, RecipeRunDB, RecipeRunState
from mestolo.recipe import Menu, Recipe


class Chef:
    def __init__(self, menu: Menu,
                 num_cooks: int,
                 session: Optional[Session] = None,
                 duration: float =   math.inf,
                 refresh_rate: float = 1.0):
        now = datetime.now()
        self._session = session or create_session()

        self._num_cooks: int = num_cooks
        self._menu: Menu = menu
        self._duration: float = duration
        self._refresh_rate: float = refresh_rate

        self._processes: List[mp.Process] = []

        self._schedule: PriorityQueue[Recipe] = PriorityQueue()

    def _cook_recipe(self, recipe_name: uuid.UUID):
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
                self._cook_recipe(self._schedule.get())
                free_cook_count -= 1

            # run the monitoring update

            # TODO: actually do the cooking!

            loop_duration = time.time() - loop_start_time
            time.sleep(max(self._refresh_rate - loop_duration, 0))

    def close(self):
        for p in self._processes:
            p.join()

    def check_for_zombies(self, recipe_name: str, sigma: float = 3.0):
        now = datetime.now()
        average_time = float(self._session.query(sa.func.avg(RecipeRunDB.end_time - RecipeRunDB.start_time))
        .filter(RecipeRunDB.status == RecipeRunState.cooked)
         .filter(RecipeRunDB.recipe_name == recipe_name).scalar())
        std_time = float(self._session.query(sa.func.stddev_samp(RecipeRunDB.end_time - RecipeRunDB.start_time))
                    .filter(RecipeRunDB.status == RecipeRunState.cooked)
                        .filter(RecipeRunDB.recipe_name == recipe_name).scalar())
        maximum_time = timedelta(minutes=(average_time + 3 * std_time)/100)
        print("max time", maximum_time)
        return self._session.query(RecipeRunDB).filter(RecipeRunDB.status == RecipeRunState.cooking).filter(RecipeRunDB.recipe_name == recipe_name).filter(now - maximum_time > RecipeRunDB.start_time).all()
