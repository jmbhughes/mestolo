import os
from dataclasses import dataclass
from datetime import datetime
from importlib.util import module_from_spec, spec_from_file_location
from typing import Any


def load_module(path):
    folder, filename = os.path.split(path)
    basename, extension = os.path.splitext(filename)
    spec = spec_from_file_location(basename, path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.__name__ == basename
    return module


def load_function(path, function_name):
    module = load_module(path)
    return getattr(module, function_name)


@dataclass
class Recipe:
    name: str
    path: str
    priority: float
    trigger: Any
    delay: float
    escalation_times: [float]
    escalation_values: [float]
    inputs: [str]
    outputs: [str]

    def cook(self, pipe):
        pipe.send(f"running {self.name}")
        f = load_function(self.path, self.name)
        f()
        pipe.send(f"finished {self.name}")

    @classmethod
    def load_from_config(cls, name, recipe_config):
        return cls(name, **recipe_config)


@dataclass
class ScheduledItem:
    schedule_time: datetime
    current_priority: float
    recipe: Recipe

    def escalate_priority(self):
        now = datetime.now()
        waiting_seconds = (now - self.schedule_time).total_seconds()
        for escalation_time, escalation_value in zip(self.recipe.escalation_times, self.recipe.escalation_values):
            if waiting_seconds > escalation_time:
                self.current_priority = escalation_value

    def __le__(self, other):
        return self.current_priority <= other.current_priority

    def __ge__(self, other):
        return self.current_priority >= other.current_priority

    def __eq__(self, other):
        return self.current_priority == other.current_priority

    def __ne__(self, other):
        return self.current_priority != other.current_priority

    def __gt__(self, other):
        return self.current_priority > other.current_priority

    def __lt__(self, other):
        return self.current_priority < other.current_priority
