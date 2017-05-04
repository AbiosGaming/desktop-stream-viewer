from constants import CONFIG_FILE, CONFIG_DEFAULT_VALUES
import json


class _Config:
    def __init__(self):
        self._values = None

        try:
            with open(CONFIG_FILE, mode='r') as cfg:
                self._values = json.load(cfg)
        except FileNotFoundError:
            print("No config file found, creating one...")
            self._values = CONFIG_DEFAULT_VALUES
            with open(CONFIG_FILE, mode='w+') as cfg:
                json.dump(self._values, cfg)
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


cfg = _Config()
