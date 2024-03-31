import os
from importlib.util import spec_from_file_location, module_from_spec


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


class Recipe:
    def __init__(self, name, path, priority, trigger, delay):
        self.name = name
        self.path = path
        self.priority = priority
        self.trigger = trigger
        self.delay = delay

    def run(self):
        print(f"running {self.name}")
        f = load_function(self.path, self.name)
        f()
        print(f"finished {self.name}")
