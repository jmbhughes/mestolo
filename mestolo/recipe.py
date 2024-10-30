import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from importlib.util import module_from_spec, spec_from_file_location
from typing import Any

from .datetime import DateTimeInterval


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
    ingredient: str
    path: str
    priority: float
    trigger: Any
    schedule: str
    escalation_times: list[float]
    escalation_values: list[float]
    inputs: list[str]
    valid_before_seconds: float | list[float] | None = None
    valid_after_seconds: float | list[float] | None = None

    def cook(self, inputs, node_id, cooked_queue, error_queue):
        try:
            f = load_function(self.path, self.name)
            output = f(*inputs)
            cooked_queue.put((self.ingredient, output, node_id))
        except KeyboardInterrupt:
            pass  # allow the chef to handle quitting
        except Exception as e:
            error_queue.put(e)

    @classmethod
    def load_from_config(cls, name, recipe_config):
        return cls(name, **recipe_config)

    def get_valid_interval(self, dt):
        if self.valid_before_seconds is None:
            start = None
        else:
            start = dt - timedelta(seconds=self.valid_before_seconds)

        if self.valid_after_seconds is None:
            end = None
        else:
            end = dt + timedelta(seconds=self.valid_after_seconds)
        return DateTimeInterval(start, end)

    @property
    def current_valid_interval(self):
        return self.get_valid_interval(datetime.now())
