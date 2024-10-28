import multiprocessing as mp
import signal
import time
from datetime import datetime
from enum import IntEnum
from queue import Empty, PriorityQueue
from random import random

import pandas as pd
from croniter import croniter
from sqlalchemy import and_

from .db import EdgesDB, NodeDB, ScheduledIngredientDB, create_session
from .ingredients import IngredientConstraint, ScheduledIngredient
from .menu import Menu


class NodeState(IntEnum):
    PLANNED = 1
    SCHEDULED = 2
    COOKING = 3
    COOKED = 4
    UNKNOWN = 5

class Chef:
    def __init__(self, menu: Menu, monitor_queue = None, schedule_queue = None):
        now = datetime.now()

        self._menu = menu
        self._croniters = {recipe.name: croniter(recipe.schedule, now) for recipe in self._menu.recipes.values()}

        self._monitor_queue = monitor_queue if monitor_queue is not None else mp.Queue()
        self._schedule_queue = schedule_queue if schedule_queue is not None else mp.Queue()

        self._scheduled_items = PriorityQueue()
        self._processes = []
        self._cooked_queue = mp.Queue()
        self._error_queue = mp.Queue()
        self._currently_ready = set()

        self._last_planned_time = {}
        # self._planning_graph = nx.DiGraph()
        # self._nodes_by_ingredient = {}
        for recipe_name, recipe in self._menu.recipes.items():
            if not recipe.inputs:
                self._plan_ingredient_now(recipe)

    def schedule_to_df(self):
        names, times, priorities = [], [], []
        new_schedule = PriorityQueue()
        while not self._scheduled_items.empty():
            item = self._scheduled_items.get()
            names.append(item.recipe.name)
            times.append(item.schedule_time)
            priorities.append(item.current_priority)
            new_schedule.put(item)
        self._scheduled_items = new_schedule
        return pd.DataFrame({'names': names, 'scheduled': times, 'priority': priorities})

    def _cook_ingredient(self, ingredient: ScheduledIngredient):
        # TODO: remove from scheduledingredientdb
        session = create_session()
        entry = session.query(ScheduledIngredientDB).where(ScheduledIngredientDB.node == ingredient.node_id).one()
        entry.active = False
        session.commit()

        p = mp.Process(target=ingredient.recipe.cook, args=(ingredient.inputs,
                                                         ingredient.node_id,
                                                         self._cooked_queue,
                                                         self._error_queue))
        self._processes.append(p)
        self._update_node_state(ingredient.node_id, NodeState.COOKING)
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
        for ingredient, output, node_id in just_produced:
            self._update_node_state(node_id, NodeState.COOKED)
            # children_nodes = [edge[1] for edge in self._planning_graph.out_edges(node)]
            children_nodes = self._get_children_nodes(node_id)
            for child in children_nodes:
                # self._planning_graph.nodes[child]['inputs'][ingredient] = output
                # TODO: handle passing inputs
                self._deactivate_edge(node_id, child.id)
            # self._planning_graph.remove_node(node)
            # self._nodes_by_ingredient[ingredient].remove(node)

    def _get_children_nodes(self, node_id):
        session = create_session()
        children_ids = session.query(EdgesDB.sink).filter(EdgesDB.active).where(EdgesDB.source == node_id).all()
        children_ids = [r[0] for r in children_ids]
        return session.query(NodeDB).where(NodeDB.id.in_(children_ids)).all()

    def _get_nodes_ready_to_cook(self):
        session = create_session()
        sink_node_ids = session.query(EdgesDB.sink).filter(EdgesDB.active).distinct().all()
        sink_node_ids = [r[0] for r in sink_node_ids]
        print("sink_node_ids", sink_node_ids)
        return (session.query(NodeDB)
                .filter(NodeDB.state == NodeState.PLANNED)
                .where(NodeDB.id.notin_(sink_node_ids))
                .all())

    def _get_number_in_state(self, state: NodeState) -> int:
        session = create_session()
        return len(session.query(NodeDB).filter(NodeDB.state == state).all())

    def _schedule_ready_to_cook(self):
        now = datetime.now()

        # nodes_with_no_inputs = [node for node, in_degree in self._planning_graph.in_degree() if in_degree == 0]
        # ready_nodes = [node for node in nodes_with_no_inputs
        #                if self._planning_graph.nodes[node].get('state', NodeState.UNKNOWN) == NodeState.PLANNED]
        ready_nodes = self._get_nodes_ready_to_cook()
        db_entries = []
        for node in ready_nodes:
            ingredient_constraint = node.to_ingredient_constraint()
            recipe = self._menu.get_recipe_for(ingredient_constraint.name)
            # inputs = self._planning_graph.nodes[ingredient_constraint].get('inputs', {})
            # TODO: get inputs somehow!
            inputs = {}
            self._scheduled_items.put(ScheduledIngredient(now, recipe.priority, recipe, inputs,
                                                          node.id))
            self._update_node_state(node.id, NodeState.SCHEDULED)
            db_entries.append(ScheduledIngredientDB(schedule_time=now,
                                                    current_priority=recipe.priority,
                                                    recipe=recipe.name,
                                                    node=node.id))
        session = create_session()
        session.add_all(db_entries)
        session.commit()

    def _get_satisfying_nodes(self, ingredient_name: str, dt: datetime):
        results = []
        #for node in self._nodes_by_ingredient[ingredient_name]:
        for node in self._get_nodes_by_ingredient(ingredient_name):
            if node.to_ingredient_constraint().valid_interval.includes(dt):
                results.append(node)
        return results

    def _get_nodes_by_ingredient(self, ingredient_name: str, allowed_states=(NodeState.PLANNED,)):
        session = create_session()
        return session.query(NodeDB).where(and_(NodeDB.name==ingredient_name,
                                         NodeDB.state.in_(allowed_states))).all()


    def _create_node(self, constraint: IngredientConstraint):
        # self._planning_graph.add_node(constraint)
        # self._planning_graph.nodes[constraint]['state'] = NodeState.PLANNED
        # self._planning_graph.nodes[constraint]['inputs'] = {}
        posx, posy = (random(), random())
        # self._planning_graph.nodes[constraint]['pos'] = (posx, posy)

        session = create_session()
        entry = NodeDB(name=constraint.name,
                       start_time=constraint.valid_interval.start,
                       end_time=constraint.valid_interval.end,
                       state = NodeState.PLANNED,
                       posx = posx,
                       posy = posy)
        session.add(entry)
        session.commit()
        return entry.id
        # self._planning_graph.nodes[constraint]['id'] = entry.id

    def _update_node_state(self,  node_id: int, new_state: NodeState):
        # self._planning_graph.nodes[constraint]['state'] = new_state
        session = create_session()
        entry = session.query(NodeDB).where(NodeDB.id == node_id).one()
        entry.state = new_state
        session.commit()

    def _create_edge(self, source_id, sink_id):
        # self._planning_graph.add_edge(source, sink)

        session = create_session()
        entry = EdgesDB(source = source_id,
                        sink = sink_id)
        session.add(entry)
        session.commit()

    def _deactivate_edge(self, source_id, sink_id):
        session = create_session()
        entry = session.query(EdgesDB).where(
            and_(EdgesDB.source == source_id,
                 EdgesDB.sink == sink_id)).one()
        entry.active = False
        session.commit()

    def _plan_ingredient_now(self, recipe):
        now = datetime.now()
        self._last_planned_time[recipe.name] = now

        node_value = IngredientConstraint(recipe.ingredient, recipe.current_valid_interval)
        node_id = self._create_node(node_value)

        # if recipe.ingredient in self._nodes_by_ingredient:
        #     self._nodes_by_ingredient[recipe.ingredient].append(node_value)
        # else:
        #     self._nodes_by_ingredient[recipe.ingredient] = [node_value]

        for input_ingredient in recipe.inputs:
            satisfying_nodes = self._get_satisfying_nodes(input_ingredient, now)
            if satisfying_nodes:
                self._create_edge(satisfying_nodes[0].id, node_id)
            else:
                new_satisfying_node = IngredientConstraint(input_ingredient, recipe.current_valid_interval)
                new_satisfying_id = self._create_node(new_satisfying_node)
                self._create_edge(new_satisfying_id, node_id)

    def _plan_ingredients(self):
        now = datetime.now()

        for recipe in self._menu.recipes.values():
            num_starts = 0
            while self._croniters[recipe.name].get_next(datetime) < now:
                num_starts += 1
            self._croniters[recipe.name].get_prev(datetime)

            print(recipe.ingredient, num_starts)

            for _ in range(num_starts):
                self._plan_ingredient_now(recipe)

    def _escalate_scheduled_priorities(self):
        new_schedule = PriorityQueue()
        while not self._scheduled_items.empty():
            item = self._scheduled_items.get()
            item.escalate_priority()
            new_schedule.put(item)
        self._scheduled_items = new_schedule

    def _monitor(self):
        # self._monitor_queue.put(self._planning_graph)
        schedule_df = self.schedule_to_df()
        print(schedule_df)
        # self._schedule_queue.put(schedule_df)

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
            loop_start_time = time.time()
            self._get_all_cooked()
            self._schedule_ready_to_cook()
            active_cooks = self._clean_processes()
            num_free_cooks = self._menu.max_simultaneous - active_cooks
            print("ACTIVE COOKS", active_cooks,
                  "SCHEDULE LENGTH", self._scheduled_items.qsize(),
                  "PLANNED COUNT", self._get_number_in_state(NodeState.PLANNED),
                  "SCHEDULED COUNT", self._get_number_in_state(NodeState.SCHEDULED),
                  "COOKING COUNT", self._get_number_in_state(NodeState.COOKING)) # len(self._planning_graph))
            while num_free_cooks > 0 and not self._scheduled_items.empty():
                self._cook_ingredient(self._scheduled_items.get())
                num_free_cooks -= 1
            self._plan_ingredients()
            self._escalate_scheduled_priorities()
            print("-" * 80)
            self._monitor()
            loop_duration = time.time() - loop_start_time
            time.sleep(max(self._menu.refresh_delay - loop_duration, 0))
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
