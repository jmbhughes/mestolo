from collections import namedtuple
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from mestolo.recipe import Recipe

IngredientInstance = namedtuple("IngredientInstance", ["name", "time", "value"])
IngredientConstraint = namedtuple("IngredientConstraint", ["name", "valid_interval"])


@dataclass
class ScheduledIngredient:
    schedule_time: datetime
    current_priority: float
    recipe: Recipe
    inputs: dict[str, Any]
    node: IngredientConstraint

    def escalate_priority(self):
        now = datetime.now()
        waiting_seconds = (now - self.schedule_time).total_seconds()
        for escalation_time, escalation_value in zip(self.recipe.escalation_times, self.recipe.escalation_values):
            if waiting_seconds > escalation_time:
                self.current_priority = escalation_value

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
