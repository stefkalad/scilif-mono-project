# Axis X Settings
import time

from app.cnc_programmer.rpi_board import RPiBoard
from app.cnc_programmer.stepper.position import Axis, PositionInSteps as PosStep

# NOTES:
# acceleration / deceleration ramp assumes movment more than 3 mm

X_STEPS_PER_MM = 320  # 200 steps per revolution x 8 microsteps = 1600 steps per revolution / 5mm per revolution -> 1600/5 = 320 steps per mm
X_MAX_SPEED = 100  # ideal reliable maximum speed (in microseconds per pulse)
X_MIN_SPEED = 500  # minimum speed (in microseconds per pulse)
X_ACC_RAMP = 400  # acceleration ramp (in pulses)
X_DECC_RAMP = 400  # deceleration ramp (in pulses)

# Axis Y Settings
Y_STEPS_PER_MM = 320  # 200 steps per revolution x 8 microsteps = 1600 steps per revolution / 5mm per revolution -> 1600/5 = 320 steps per mm
Y_MAX_SPEED = 100  # ideal reliable maximum speed (in microseconds per pulse)
Y_MIN_SPEED = 500  # minimum speed (in microseconds per pulse)
Y_ACC_RAMP = 400  # acceleration ramp (in pulses)
Y_DECC_RAMP = 400  # deceleration ramp (in pulses)

# Axis Z Settings
Z_STEPS_PER_MM = 400  # 200 steps per revolution x 8 microsteps = 1600 steps per revolution / 4mm per revolution -> 1600/4 = 400 steps per mm
Z_MAX_SPEED = 100  # ideal reliable maximum speed (in microseconds per pulse)
Z_MIN_SPEED = 500  # minimum speed (in microseconds per pulse)
Z_ACC_RAMP = 400  # acceleration ramp (in pulses)
Z_DECC_RAMP = 400  # deceleration ramp (in pulses)

X_AXIS_SPECIFICATION = {
    'steps_per_mm': X_STEPS_PER_MM,
    'max_speed': X_MAX_SPEED,
    'min_speed': X_MIN_SPEED,
    'acc_ramp': X_ACC_RAMP,
    'decc_ramp': X_DECC_RAMP,
}

Y_AXIS_SPECIFICATION = {
    'steps_per_mm': Y_STEPS_PER_MM,
    'max_speed': Y_MAX_SPEED,
    'min_speed': Y_MIN_SPEED,
    'acc_ramp': Y_ACC_RAMP,
    'decc_ramp': Y_DECC_RAMP,
}

Z_AXIS_SPECIFICATION = {
    'steps_per_mm': Z_STEPS_PER_MM,
    'max_speed': Z_MAX_SPEED,
    'min_speed': Z_MIN_SPEED,
    'acc_ramp': Z_ACC_RAMP,
    'decc_ramp': Z_DECC_RAMP,
}


def get_axis_params(axis: Axis) -> dict[str, int]:
    if axis == Axis.X:
        return X_AXIS_SPECIFICATION
    if axis == Axis.Y:
        return Y_AXIS_SPECIFICATION
    if axis == Axis.Z:
        return Z_AXIS_SPECIFICATION


class StepperDriver:

    def __init__(self, board: RPiBoard) -> None:
        self.board = board
        self.pos_current_step = PosStep()
        self.running = False

    def get_current_pos(self) -> [int, int, int]:
        return self.pos_current_step.pos

    def reset_pos(self) -> None:
        self.pos_current_step.reset()

    def get_current_pos_mm(self) -> [float, float, float]:
        return [self.pos_current_step.to_mm(Axis.X, get_axis_params(Axis.X)['steps_per_mm']),
                self.pos_current_step.to_mm(Axis.Y, get_axis_params(Axis.Y)['steps_per_mm']),
                self.pos_current_step.to_mm(Axis.Z, get_axis_params(Axis.Z)['steps_per_mm'])]

    # Move to absolute position in step, speed in % of maximum speed
    def go_to_pos_step(self, axis: Axis, pos_target_axis_step: int, speed_percent: float, wait_time: float = 0.0) -> bool:
        axis_params: dict[str, int] = get_axis_params(axis)
        delta_step: int = pos_target_axis_step - self.pos_current_step.get(axis)

        # break condition
        if delta_step == 0:
            return True

        # convert speed from percentage to microseconds
        if speed_percent > 100:
            speed_percent = 100
        elif speed_percent <= 0:
            return False
        speed_target_us: int = round((axis_params['min_speed'] - axis_params['max_speed']) * (100 - speed_percent) / 100 + axis_params['max_speed'])

        # helper variable to determine whether to increment or decrement the current position
        direction: bool = delta_step > 0
        # switch the direction output
        self.board.stepper_dir_pins[axis.value].value = (not direction)

        speed_current_us: int = axis_params['min_speed']

        # wait before start
        time.sleep(wait_time)

        # move by the specified number of steps
        for i in range(abs(delta_step)):
            # break condition
            if not self.running: return True
            # deceleration
            if (abs(delta_step) - i) <= axis_params['decc_ramp']:
                speed_current_us = round(
                    axis_params['min_speed'] - (axis_params['min_speed'] - axis_params['max_speed']) * (abs(delta_step) - i) / axis_params['decc_ramp'])
                # if the target speed is greater (lower in value) than the calculated speed --> use target speed
                if speed_current_us < speed_target_us:
                    speed_current_us = speed_target_us

            # acceleration
            if i <= axis_params['acc_ramp']:
                speed_current_us = round(axis_params['min_speed'] - (axis_params['min_speed'] - axis_params['max_speed']) * i / axis_params['acc_ramp'])
                # if the target speed is greater (lower in value) than the calculated speed --> use target speed
                if speed_current_us < speed_target_us:
                    speed_current_us = speed_target_us

            # switch the step pin
            self.board.stepper_step_pins[axis.value].value = True
            time.sleep(speed_current_us / 1000000.0)
            self.board.stepper_step_pins[axis.value].value = False
            time.sleep(speed_current_us / 1000000.0)

            self.pos_current_step.increment(axis, 1 if direction else -1)
        return True

    # Move to absolute position in mm, speed in % of maximum speed
    def go_to_pos_mm(self, axis: Axis, pos_target_axis_mm: float, speed_percent: float, wait_time: float = 0.0) -> bool:
        axis_params: dict[str, int] = get_axis_params(axis)
        pos_target_axis_step: int = round(pos_target_axis_mm * axis_params['steps_per_mm'])
        return self.go_to_pos_step(axis, pos_target_axis_step, speed_percent, wait_time)

    def move(self, axis: Axis, step_mm: float, speed_percent: float) -> bool:
        axis_params: dict[str, int] = get_axis_params(axis)
        delta_step: int = round(step_mm * axis_params['steps_per_mm'])
        return self.go_to_pos_step(axis, self.pos_current_step.get(axis) + delta_step, speed_percent)


    def go_home(self, speed_percent: float) -> bool:
        if self.pos_current_step.is_home():
            return True
        return (self.go_to_pos_step(Axis.X, 0, speed_percent) and
                self.go_to_pos_step(Axis.Y, 0, speed_percent) and
                self.go_to_pos_step(Axis.Z, 0, speed_percent))

def test():
    board = RPiBoard()
    stepper_driver = StepperDriver(board)
    stepper_driver.go_to_pos_mm(Axis.X, -100, 75)
    stepper_driver.go_to_pos_mm(Axis.Y, -100, 75)
    stepper_driver.go_to_pos_mm(Axis.Z, 10, 30)
    # stepper_driver.go(Axis.X, -50, 100)
    # stepper_driver.go(Axis.X, 50, 100)
    # stepper_driver.go(Axis.X, -50, 100)
    # stepper_driver.go(Axis.X, 100, 100)
    # stepper_driver.go(Axis.Y, -100, 100)
    # stepper_driver.go(Axis.Y, 100, 100)
    # stepper_driver.go(Axis.Z, 20, 100)
    # stepper_driver.go(Axis.Z, -20, 100)
    # stepper_driver.go(Axis.X, 50, 100)


def test2():
    print("TEst2")
    board = RPiBoard()
    axis = Axis.Y.value
    stepper_driver = StepperDriver(board)
    board.stepper_dir_pins[axis].value = True
    speed_current_us = X_MIN_SPEED
    while True:
        board.stepper_step_pins[axis].value = True
        time.sleep(speed_current_us / 1000000.0)
        board.stepper_step_pins[axis].value = False
        time.sleep(speed_current_us / 1000000.0)


def test3():
    print("TEST3")
    board = RPiBoard()
    axis = Axis.Y.value
    stepper_driver = StepperDriver(board)

    while True:
        board.stepper_dir_pins[axis].value = True
        board.stepper_step_pins[axis].value = True
        time.sleep(2)
        board.stepper_dir_pins[axis].value = False
        board.stepper_step_pins[axis].value = False
        time.sleep(2)


def test_on_keyboard_input():
    board = RPiBoard()
    axis = Axis.Z
    stepper_driver = StepperDriver(board)
    stepper_driver.go_to_pos_mm(axis, 10, 100)

    # keyboard.on_press_key("down", lambda _: stepper_driver.go(axis, -1.0, 100))
    #
    #
    # # Keep the script running
    # keyboard.wait("esc")  # Press "Esc" to exit the script
    # pass


if __name__ == "__main__":
    test_on_keyboard_input()
