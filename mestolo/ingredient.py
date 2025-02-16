from collections import namedtuple
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from mestolo.recipe import Recipe

IngredientInstance = namedtuple("IngredientInstance", ["name", "time", "value"])

@dataclass
class ScheduledIngredient:
    schedule_time: datetime
    current_priority: float
    recipe: Recipe
    inputs: dict[str, Any]
    node_id: int

    def __le__(self, other):
        return self.__eq__(other) or self.__le__(other)

    def __ge__(self, other):
        return self.__eq__(other) or self.__gt__(other)

    def __eq__(self, other):
        return self.current_priority == other.current_priority

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        return self.current_priority > other.current_priority

    def __lt__(self, other):
        return self.current_priority < other.current_priority
