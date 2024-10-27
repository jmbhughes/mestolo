import multiprocessing
import signal
import time
from datetime import datetime
from enum import Enum
from multiprocessing import Process
from queue import Empty, PriorityQueue

import networkx as nx

from .ingredients import IngredientConstraint, ScheduledIngredient
from .menu import Menu

NodeState = Enum("NodeStates", ['PLANNED', 'SCHEDULED', 'COOKING', 'COOKED', 'UNKNOWN'])

class Chef:
    def __init__(self, menu: Menu):
        self._menu = menu

        self._scheduled_items = PriorityQueue()
        self._processes = []
        self._cooked_queue = multiprocessing.Queue()
        self._error_queue = multiprocessing.Queue()
        self._currently_ready = set()

        self._last_scheduled = {}
        self._planning_graph = nx.DiGraph()
        self._nodes_by_ingredient = {}
        for recipe_name, recipe in self._menu.recipes.items():
            if not recipe.inputs:
                self._plan_ingredient_now(recipe)

    def _cook_ingredient(self, ingredient: ScheduledIngredient):
        p = Process(target=ingredient.recipe.cook, args=(ingredient.inputs,
                                                         ingredient.node,
                                                         self._cooked_queue,
                                                         self._error_queue))
        self._processes.append(p)
        self._planning_graph.nodes[ingredient.node]['state'] = NodeState.COOKING
        p.start()

    def _clean_processes(self):
        self._processes = [p for p in self._processes if p.is_alive()]
        return len(self._processes)

    def _get_all_cooked(self):
        just_produced = []
        while True:
            try:
                just_produced.append(self._cooked_queue.get(block=False))
            except Empty:
                break
        for ingredient, output, node in just_produced:
            children_nodes = [edge[1] for edge in self._planning_graph.out_edges(node)]
            for child in children_nodes:
                self._planning_graph.nodes[child]['inputs'][ingredient] = output
            self._planning_graph.remove_node(node)
            self._nodes_by_ingredient[ingredient].remove(node)

    def _schedule_ready_to_cook(self):
        now = datetime.now()

        nodes_with_no_inputs = [node for node, in_degree in self._planning_graph.in_degree() if in_degree == 0]
        ready_nodes = [node for node in nodes_with_no_inputs
                       if self._planning_graph.nodes[node].get('state', NodeState.UNKNOWN) == NodeState.PLANNED]
        for ingredient_constraint in ready_nodes:
            recipe = self._menu.get_recipe_for(ingredient_constraint.name)
            self._last_scheduled[recipe.name] = now
            inputs = self._planning_graph.nodes[ingredient_constraint].get('inputs', {})
            self._scheduled_items.put(ScheduledIngredient(now, recipe.priority, recipe, inputs,
                                                          ingredient_constraint))
            self._planning_graph.nodes[ingredient_constraint]['state'] = NodeState.SCHEDULED

    def _get_satisfying_nodes(self, ingredient_name: str, dt: datetime):
        results = []
        for node in self._nodes_by_ingredient[ingredient_name]:
            if node.valid_interval.includes(dt):
                results.append(node)
        return results

    def _plan_ingredient_now(self, recipe):
        now = datetime.now()
        node_value = IngredientConstraint(recipe.ingredient, recipe.current_valid_interval)
        self._planning_graph.add_node(node_value)
        self._planning_graph.nodes[node_value]['state'] = NodeState.PLANNED
        self._planning_graph.nodes[node_value]['inputs'] = {}

        if recipe.ingredient in self._nodes_by_ingredient:
            self._nodes_by_ingredient[recipe.ingredient].append(node_value)
        else:
            self._nodes_by_ingredient[recipe.ingredient] = [node_value]

        for input_ingredient in recipe.inputs:
            satisfying_nodes = self._get_satisfying_nodes(input_ingredient, now)
            if satisfying_nodes:
                self._planning_graph.add_edge(node_value, satisfying_nodes[0])
            else:
                new_satisfying_node = IngredientConstraint(input_ingredient, recipe.current_valid_interval)
                self._planning_graph.add_node(new_satisfying_node)
                self._planning_graph.add_edge(new_satisfying_node, node_value)

    def _plan_ingredients(self):
        now = datetime.now()

        for recipe in self._menu.recipes.values():
            last_time = self._last_scheduled.get(recipe.name, None)
            has_delayed_enough = (now - last_time).total_seconds() > recipe.delay if last_time is not None else True
            if has_delayed_enough:
                self._plan_ingredient_now(recipe)

    def _escalate_scheduled_priorities(self):
        new_schedule = PriorityQueue()
        while not self._scheduled_items.empty():
            item = self._scheduled_items.get()
            item.escalate_priority()
            new_schedule.put(item)
        self._scheduled_items = new_schedule

    def close(self):
        for process in self._processes:
            process.join()
        self._cooked_queue.close()
        found_errors = self.errors
        self._error_queue.close()
        return found_errors

    def cook(self):
        running = True

        def handler(this_signal, frame):
            print("STOPPING")
            nonlocal running
            running = False

        signal.signal(signal.SIGINT, handler)
        start = time.time()
        while running and time.time() - start < self._menu.duration:
            self._get_all_cooked()
            self._schedule_ready_to_cook()
            active_cooks = self._clean_processes()
            num_free_cooks = self._menu.max_simultaneous - active_cooks
            print("ACTIVE COOKS", active_cooks,
                  "SCHEDULE LENGTH", self._scheduled_items.qsize(),
                  "NODE COUNT", len(self._planning_graph))
            while num_free_cooks > 0 and not self._scheduled_items.empty():
                self._cook_ingredient(self._scheduled_items.get())
                num_free_cooks -= 1
            self._plan_ingredients()
            self._escalate_scheduled_priorities()
            print("-" * 80)
            time.sleep(self._menu.refresh_delay)
        else:
            errors = self.close()
            print("Errors:", errors)
        return errors

    @property
    def errors(self):
        found_errors = []
        while True:
            try:
                found_errors.append(self._error_queue.get(block=False))
            except Empty:
                break
        return found_errors
