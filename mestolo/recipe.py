from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Callable, Optional, Dict
from typing import List
import uuid
from datetime import datetime, timedelta, timezone
import math

from sqlalchemy.orm import Session

from mestolo.db import RecipeRun, RecipeRunState
from mestolo.error import MenuError
from mestolo.selector import SelectorABC


def recipe(inputs: Dict[str, SelectorABC],
           outputs: List[str],
           cadence: timedelta,
           lookback_length: timedelta = timedelta(days=1),
           menus: Optional[List[Menu]] = None,
           priority: float = 1):
    def decorator_recipe(func):
        signature = inspect.signature(func)

        # make sure the function signature matches the decorator inputs
        required_signature_params = set(name for name, param in signature.parameters.items()
                                        if param.default is inspect.Parameter.empty)
        if set([name for name in inputs]) != required_signature_params:
            raise RuntimeError("Constraints must match the function signatures.")

        r = Recipe(func.__name__,
                   func,
                   inputs,
                   outputs,
                   cadence,
                   lookback_length,
                   priority)

        # try to add it to the menus
        if menus is not None:
            for menu in menus:
                menu.add(r)

        return r
    return decorator_recipe

@dataclass
class Recipe:
    name: str
    func: Callable
    inputs: Dict[str, SelectorABC]
    outputs: List[str]
    cadence: timedelta
    lookback_length: timedelta = timedelta(days=1)
    priority: float = 1

    def check_cooking_status(self, dt: datetime, session: Session) -> RecipeRunState:
        pass

    def determine_cook_schedule(self, dt: datetime, session: Session) -> List[datetime]:
        pass

    def last_cooked_time(self, session: Session) -> Optional[datetime]:
        # TODO: actually filter by this recipe name... it shouldn't be static
        result = session.query(RecipeRun).filter(RecipeRun.status == 1).order_by(RecipeRun.end_time).first()
        return None if result is None else result.end_time


    def cook(self, cooked_queue, error_queue, session: Session, dt=datetime.now(timezone.utc)):
        # TODO : use selectors!
        # TODO: this should only be called in a chef.cook environment
        # call_times = self.calculate_lookback_schedule(dt)
        # for call_time in call_times:
        # try:
        #     actual_outputs = self(*inputs)
        #     for output_name, output_value in zip(actual_outputs, self.outputs):
        #         cooked_queue.put((output_name, output_value, node_id))
        # except KeyboardInterrupt:
        #     pass  # allow the chef to handle quitting
        # except Exception as e:
        #     error_queue.put(e)
        pass

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def calculate_lookback_schedule(self, dt: datetime) -> List[datetime]:
        start_time = dt - self.lookback_length
        num_expected = int(math.ceil((dt - start_time) / self.cadence))
        return [start_time + i * self.cadence for i in range(num_expected)]


class Menu:
    def __init__(self, recipes: List[Recipe]):
        self._recipes = {uuid.uuid4(): r for r in recipes}

        self._recipes_by_output = {}
        self._recipes_by_input = {}
        for recipe_id, r in self._recipes.items():
            for in_ingredient in r.inputs:
                if in_ingredient in self._recipes_by_input:
                    self._recipes_by_input[in_ingredient].append(recipe_id)
                else:
                    self._recipes_by_input[in_ingredient] = [recipe_id]

            for out_ingredient in r.outputs:
                if out_ingredient in self._recipes_by_output:
                    self._recipes_by_output[out_ingredient].append(recipe_id)
                else:
                    self._recipes_by_output[out_ingredient] = [recipe_id]


        ingredients_without_recipes = self.all_ingredients.difference(set(self._recipes_by_output.keys()))
        if ingredients_without_recipes:
            msg = f"Some ingredients didn't have recipes that produced them: {ingredients_without_recipes}."
            raise MenuError(msg)

    @property
    def recipes(self):
        return self._recipes

    @property
    def all_ingredients(self):
        all_ingredients = set()
        for r in self.recipes.values():
            all_ingredients.update(set(r.inputs))
            all_ingredients.update(set(r.outputs))
        return all_ingredients

    def get_recipes_making(self, ingredient: str) -> List[Recipe]:
        return [self._recipes[recipe_id] for recipe_id in self._recipes_by_output[ingredient]]

    def get_recipes_requiring(self, ingredient: str) -> List[Recipe]:
        return [self._recipes[recipe_id] for recipe_id in self._recipes_by_input[ingredient]]


    def add(self, r: Recipe):
        guid = uuid.uuid4()
        self._recipes[guid] = r
        for ingredient in r.inputs:
            if ingredient in self._recipes_by_input:
                self._recipes_by_input[ingredient].append(guid)
            else:
                self._recipes_by_input[ingredient] = [guid]

        for ingredient in r.outputs:
            if ingredient in self._recipes_by_output:
                self._recipes_by_output[ingredient].append(guid)
            else:
                self._recipes_by_output[ingredient] = [guid]

    def __getitem__(self, item: uuid.UUID):
        return self._recipes[item]
