from enum import Enum


class FirmwareType(Enum):
    MAX_ONLY = "MAX_ONLY"
    FLASH = "FLASH"

class DPSMode(Enum):
    @classmethod
    def increase_mode(cls, mode):
        return cls((mode.value + 1) % len(cls))


class DPSMaxOnlyMode(DPSMode):
    NO = 0
    STRONG = 1



class DPSFlashMode(DPSMode):
    STRONG = 0
    LIGHT = 1
    BLINKING = 2
