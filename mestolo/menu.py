import toml

from .constants import (DEFAULT_DURATION, DEFAULT_REFRESH_DELAY,
                        DEFAULT_SIMULTANEOUS_RATE)
from .error import MenuError
from .recipe import Recipe


class Menu:
    def __init__(self, toml_contents):
        self._contents = toml_contents
        self._recipes = {function: Recipe.load_from_config(function, config)
                         for function, config in self._contents['recipe'].items()}
        self._ingredients2functions = {recipe.ingredient: recipe.name for recipe in self._recipes.values()}

        ingredients_without_recipes = self.all_ingredients.difference(set(self._ingredients2functions.keys()))
        if ingredients_without_recipes:
            msg = f"Some ingredients didn't have recipes that produced them: {ingredients_without_recipes}."
            raise MenuError(msg)

    @property
    def recipes(self):
        return self._recipes

    @property
    def max_simultaneous(self):
        return self._contents.get('max_simultaneous', DEFAULT_SIMULTANEOUS_RATE)

    @property
    def refresh_delay(self):
        return self._contents.get('refresh_delay', DEFAULT_REFRESH_DELAY)

    @property
    def duration(self):
        return self._contents.get('duration', DEFAULT_DURATION)

    @property
    def all_ingredients(self):
        all_ingredients = set()
        for recipe in self.recipes.values():
            all_ingredients.update(set(recipe.inputs))
            all_ingredients.add(recipe.ingredient)
        return all_ingredients

    @classmethod
    def load_toml(cls, path):
        with open(path) as f:
            system_config = toml.load(f)
        return cls(system_config)

    def get_recipe_for(self, ingredient: str) -> Recipe:
        return self._recipes[self._ingredients2functions[ingredient]]
