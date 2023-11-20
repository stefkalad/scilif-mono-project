import time

import board
from busio import I2C
from digitalio import Direction, DigitalInOut, Pull


class RPiBoard:
    PIN_I2C_SCL = board.SCL
    PIN_I2C_SDA = board.SDA

    PIN_BINDER_OUTPUT = board.D13 #odjistit == 1
    PIN_MOVEMENT_AXIS_1_OUTPUT = board.D5 #vysunout
    PIN_MOVEMENT_AXIS_2_OUTPUT = board.D6 #stisknout

    PIN_BINDER_INPUT = board.D20 #zajisteno
    PIN_START_INPUT = board.D19
    PIN_MOVEMENT_AXIS_1_INPUT = board.D16 #vysunuto
    PIN_MOVEMENT_AXIS_2_INPUT = board.D26 # palec nahore

    WAIT_TIME_AFTER_INPUT_READ = 0.5

    def __init__(self) -> None:
        self.init_I2C()

        self.start_in_pin = DigitalInOut(RPiBoard.PIN_START_INPUT)
        self.start_in_pin.direction = Direction.INPUT
        self.start_in_pin.pull = Pull.DOWN

        self.binder_out_pin = DigitalInOut(RPiBoard.PIN_BINDER_OUTPUT)
        self.binder_out_pin.direction = Direction.OUTPUT
        self.binder_in_pin = DigitalInOut(RPiBoard.PIN_BINDER_INPUT)
        self.binder_in_pin.direction = Direction.INPUT
        self.binder_in_pin.pull = Pull.DOWN

        self.axis_1_movement_out_pin = DigitalInOut(RPiBoard.PIN_MOVEMENT_AXIS_1_OUTPUT)
        self.axis_1_movement_out_pin.direction = Direction.OUTPUT
        self.axis_1_movement_in_pin = DigitalInOut(RPiBoard.PIN_MOVEMENT_AXIS_1_INPUT)
        self.axis_1_movement_in_pin.direction = Direction.INPUT
        self.axis_1_movement_in_pin.pull = Pull.DOWN

        self.axis_2_movement_out_pin = DigitalInOut(RPiBoard.PIN_MOVEMENT_AXIS_2_OUTPUT)
        self.axis_2_movement_out_pin.direction = Direction.OUTPUT
        self.axis_2_movement_in_pin = DigitalInOut(RPiBoard.PIN_MOVEMENT_AXIS_2_INPUT)
        self.axis_2_movement_in_pin.direction = Direction.INPUT
        self.axis_2_movement_in_pin.pull = Pull.DOWN

    def init_I2C(self) -> None:
        self.i2c = I2C(RPiBoard.PIN_I2C_SCL, RPiBoard.PIN_I2C_SDA)


    def write_pin(self, pin: DigitalInOut, value: bool) -> None:
        print(f"Writing {value} to pin {pin._pin}")
        pin.value = value


def test_read_pins():
    b = RPiBoard()
    print("Reading pins...")
    print(f"START: {b.start_in_pin.value}")
    print(f"Binder: {b.binder_in_pin.value}")
    print(f"Axis movement 1: {b.axis_1_movement_in_pin.value}")
    print(f"Axis movement 2: {b.axis_2_movement_in_pin.value}")


#TODO: 200ms delay mezi stavy
def write_pin():
    b = RPiBoard()

    b.axis_1_movement_out_pin.value = True
    b.axis_2_movement_out_pin.value = False
    time.sleep(1)
    b.axis_1_movement_out_pin.value = True
    b.axis_2_movement_out_pin.value = True
    time.sleep(4)
    b.axis_1_movement_out_pin.value = True
    b.axis_2_movement_out_pin.value = False
    time.sleep(1)
    b.axis_1_movement_out_pin.value = False
    b.axis_2_movement_out_pin.value = False



if __name__ == "__main__":
    write_pin()
