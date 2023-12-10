from enum import Enum


class CNCRunnerState(Enum):
    STOPPED = 0
    MOVING_BY_STEP = 1
    MOVING_HOME = 2
    IN_AUTOMATIC_CYCLE = 3
    PAUSED_IN_AUTOMATIC_CYCLE = 4
    COMPLETED_AUTOMATIC_CYCLE = 5

