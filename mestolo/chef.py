import multiprocessing
import time
from datetime import datetime
from multiprocessing import Process
from queue import PriorityQueue

import networkx as nx

from .menu import Menu
from .recipe import Recipe, ScheduledItem


class Chef:
    def __init__(self, menu: Menu):
        self._menu = menu

        self._scheduled_items = PriorityQueue()
        self._processes = []
        self._pipes = []

        self._all_recipes = {}
        self._last_scheduled = {}
        self._recipe_graph = nx.DiGraph()
        self._recipe_graph.add_nodes_from(menu.all_ingredients)
        for recipe_name, recipe_object in self._menu.recipes.items():
            self._all_recipes[recipe_name] = recipe_object
            for input_ingredient in recipe_object.inputs:
                for output in recipe_object.outputs:
                    self._recipe_graph.add_edge(input_ingredient, output)

            # recipes with no inputs can be scheduled instantly
            if not recipe_object.inputs:
                now = datetime.now()
                self._scheduled_items.put(ScheduledItem(now, recipe_object.priority, recipe_object))
                self._last_scheduled[recipe_name] = now

    def _cook_recipe(self, recipe: Recipe):
        print(f"cooking {recipe.name}")
        parent_conn, child_conn = multiprocessing.Pipe()

        p = Process(target=recipe.cook, args=(child_conn,))
        self._processes.append(p)
        self._pipes.append(parent_conn)
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
        start = time.time()
        while time.time() - start < self._menu.duration:
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
