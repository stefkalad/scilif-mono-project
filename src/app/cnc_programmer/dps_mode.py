from enum import Enum


class DPSMode(Enum):
    STRONG = 0
    LIGHT = 1
    BLINKING = 2

    @classmethod
    def increase_mode(cls, mode):
        return cls((mode.value + 1) % len(DPSMode))
