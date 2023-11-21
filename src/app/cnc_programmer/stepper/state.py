from enum import Enum


class CNCRunnerState(Enum):
    STOPPED = 0
    MOVING_BY_STEP = 1
    MOVING_HOME = 2
    AUTOMATIC_CYCLE = 3

