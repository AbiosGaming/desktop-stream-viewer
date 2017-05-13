from enum import Enum


class OS(Enum):
    LINUX = "linux"
    WINDOWS = "windows"
    MAC_OS = "darwin"

    def __str__(self):
        return str(self.value)

    def __eq__(self, other):
        return isinstance(other, str) and other == str(self.value)
