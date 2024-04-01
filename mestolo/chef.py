import time
from datetime import datetime
from multiprocessing import Process
from queue import PriorityQueue

from .menu import Menu
from .recipe import Recipe, ScheduledItem


class Chef:
    def __init__(self, menu: Menu):
        self._menu = menu

        self._scheduled_items = PriorityQueue()
        self._processes = []

        self._all_recipes = {}
        self._last_scheduled = {}
        for recipe_name, recipe_config in self._menu.recipes.items():
            recipe = Recipe.load_from_config(recipe_name, recipe_config)
            self._all_recipes[recipe_name] = recipe

            now = datetime.now()
            self._scheduled_items.put(ScheduledItem(now, recipe.priority, recipe))
            self._last_scheduled[recipe_name] = now

    def _cook_recipe(self, recipe: Recipe):
        print(f"cooking {recipe.name}")
        p = Process(target=recipe.cook)
        self._processes.append(p)
        p.start()

    def _clean_processes(self):
        self._processes = [p for p in self._processes if p.is_alive()]
        return len(self._processes)

    def _schedule_recipes(self):
        now = datetime.now()
        for recipe_name, last_time in self._last_scheduled.items():
            recipe = self._all_recipes[recipe_name]
            if (now - last_time).total_seconds() > recipe.delay:
                self._last_scheduled[recipe_name] = now
                self._scheduled_items.put(ScheduledItem(now, recipe.priority, recipe))

    def _escalate_scheduled_priorities(self):
        new_schedule = PriorityQueue()
        while not self._scheduled_items.empty():
            item = self._scheduled_items.get()
            item.escalate_priority()
            new_schedule.put(item)
        self._scheduled_items = new_schedule

    def cook(self):
        while True:
            active_cooks = self._clean_processes()
            num_free_cooks = self._menu.max_simultaneous - active_cooks
            print("ACTIVE COOKS", active_cooks, "SCHEDULE LENGTH", self._scheduled_items.qsize())
            while num_free_cooks > 0 and not self._scheduled_items.empty():
                self._cook_recipe(self._scheduled_items.get().recipe)
                num_free_cooks -= 1
            self._schedule_recipes()
            self._escalate_scheduled_priorities()
            print("-" * 80)
            time.sleep(self._menu.refresh_delay)
