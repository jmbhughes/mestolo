import toml

from .constants import DEFAULT_REFRESH_DELAY, DEFAULT_SIMULTANEOUS_RATE


class Menu:
    def __init__(self, toml_contents):
        self._contents = toml_contents

    @property
    def recipes(self):
        return self._contents['recipe']

    @property
    def max_simultaneous(self):
        return self._contents.get('max_simultaneous', DEFAULT_SIMULTANEOUS_RATE)

    @property
    def refresh_delay(self):
        return self._contents.get('refresh_delay', DEFAULT_REFRESH_DELAY)

    @classmethod
    def load_toml(cls, path):
        system_config = toml.load(path)
        return cls(system_config)
