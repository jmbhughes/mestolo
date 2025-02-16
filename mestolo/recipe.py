from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Callable, Optional, Dict
from typing import List
import uuid

from mestolo.error import MenuError
from mestolo.selector import SelectorABC


def recipe(inputs: List[str],
           outputs: List[str],
           menus: Optional[List[Menu]] = None,
           selectors: Optional[Dict[str, SelectorABC]] = None,
           schedule: Optional[str] = None,
           priority: float = 1):
    def decorator_recipe(func):
        signature = inspect.signature(func)

        # make sure the function signature matches the decorator inputs
        required_signature_params = set(name for name, param in signature.parameters.items()
                                        if param.default is inspect.Parameter.empty)
        if set([name for name in inputs]) != required_signature_params:
            raise RuntimeError("Constraints must match the function signatures.")

        # TODO: make sure the selector keys match the inputs

        r = Recipe(func.__name__, func, inputs, outputs, selectors, priority, schedule)

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
    inputs: List[str]
    outputs: List[str]
    selectors: Optional[Dict[str, SelectorABC]]
    priority: float
    schedule: str

    def cook(self, inputs, node_id, cooked_queue, error_queue):
        # TODO : use selectors!
        try:
            actual_outputs = self(*inputs)
            for output_name, output_value in zip(actual_outputs, self.outputs):
                cooked_queue.put((output_name, output_value, node_id))
        except KeyboardInterrupt:
            pass  # allow the chef to handle quitting
        except Exception as e:
            error_queue.put(e)

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)



class Menu:
    def __init__(self, recipes: List[Recipe]):
        self._recipes = {uuid.uuid4(): r for r in recipes}

        self._ingredient_to_recipe_id = {}
        for recipe_id, r in self._recipes.items():
            for output in r.outputs:
                if output in self._ingredient_to_recipe_id:
                    self._ingredient_to_recipe_id[output].append(recipe_id)
                else:
                    self._ingredient_to_recipe_id[output] = [recipe_id]

        ingredients_without_recipes = self.all_ingredients.difference(set(self._ingredient_to_recipe_id.keys()))
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

    def get_recipes_for(self, ingredient: str) -> List[Recipe]:
        return [self._recipes[recipe_id] for recipe_id in self._ingredient_to_recipe_id[ingredient]]

    def add(self, r: Recipe):
        guid = uuid.uuid4()
        self._recipes[guid] = r
        for ingredient in r.outputs:
            if ingredient in self._ingredient_to_recipe_id:
                self._ingredient_to_recipe_id[ingredient].append(guid)
            else:
                self._ingredient_to_recipe_id[ingredient] = [guid]

    def __getitem__(self, item: uuid.UUID):
        return self._recipes[item]
