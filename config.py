import json
from constants import CONFIG_FILE, CONFIG_DEFAULT_VALUES


class _Config:
    def __init__(self):
        self._values = None

        try:
            self.load()
        except FileNotFoundError:
            print("No config file found, creating one...")
            self._values = CONFIG_DEFAULT_VALUES
            self.dump()
        except json.decoder.JSONDecodeError:
            print("There was an error while loading config, using default config instead.")
            self._values = CONFIG_DEFAULT_VALUES

    def __getitem__(self, key):
        if key in self._values:
            return self._values[key]
        else:
            raise ValueError("Tried to access config value that does not exist: " + key)

    def __setitem__(self, key, value):
        self._values[key] = value

    def load(self):
        """Loads the config file. Exceptions are not handled"""
        with open(CONFIG_FILE, mode='r') as f:
            self._values = json.load(f)

    def dump(self):
        """Dumps the config to the config file. Exceptions are not handled"""
        with open(CONFIG_FILE, mode='w+') as f:
            json.dump(self._values, f)


cfg = _Config()
