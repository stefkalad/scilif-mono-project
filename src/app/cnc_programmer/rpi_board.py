import time
import board
from busio import I2C
from digitalio import Direction, DigitalInOut


class RPiBoard:
    PIN_I2C_SCL = board.SCL
    PIN_I2C_SDA = board.SDA

    PIN_DSP_PGD = board.D22
    PIN_DSP_PGC = board.D27

    PIN_DSP_BUTTON = board.D18
    PIN_DSP_POWER_SUPPLY = board.D23

    # Pin Definitions
    PIN_STEPPER_X_DIR = board.D20  # Output 0 -> X goes left
    PIN_STEPPER_X_STEP = board.D21
    PIN_STEPPER_Y_DIR = board.D6  # Output 0 -> Y goes positive (from operator)
    PIN_STEPPER_Y_STEP = board.D13
    PIN_STEPPER_Z_DIR = board.D19  # Output 0 -> Z goes up
    PIN_STEPPER_Z_STEP = board.D26

    def __init__(self) -> None:
        self.init_I2C()

        # stepper
        stepper_x_dir_pin = DigitalInOut(RPiBoard.PIN_STEPPER_X_DIR)
        stepper_y_dir_pin = DigitalInOut(RPiBoard.PIN_STEPPER_Y_DIR)
        stepper_z_dir_pin = DigitalInOut(RPiBoard.PIN_STEPPER_Z_DIR)
        self.stepper_dir_pins = (stepper_x_dir_pin, stepper_y_dir_pin, stepper_z_dir_pin)

        stepper_x_step_pin = DigitalInOut(RPiBoard.PIN_STEPPER_X_STEP)
        stepper_y_step_pin = DigitalInOut(RPiBoard.PIN_STEPPER_Y_STEP)
        stepper_z_step_pin = DigitalInOut(RPiBoard.PIN_STEPPER_Z_STEP)
        self.stepper_step_pins: (DigitalInOut, DigitalInOut, DigitalInOut) = (stepper_x_step_pin, stepper_y_step_pin, stepper_z_step_pin)

        for pin in self.stepper_dir_pins + self.stepper_step_pins:
            pin.direction = Direction.OUTPUT

        # DSP power supply
        self.dsp_power_supply_pin = DigitalInOut(RPiBoard.PIN_DSP_POWER_SUPPLY)
        self.dsp_power_supply_pin.direction = Direction.OUTPUT

        # DSP button
        self.dsp_button_pin = DigitalInOut(RPiBoard.PIN_DSP_BUTTON)
        self.dsp_button_pin.direction = Direction.OUTPUT

        # DSP ICSP programmer
        self.dsp_pgd_pin = None
        self.dsp_pgc_pin = None

        # Note: set button to HIGH to prevent click emulation
        self.dsp_button_pin.value = True

    def dsp_activate(self) -> None:
        self.dsp_power_supply_pin.value = False

    def dsp_inactivate(self) -> None:
        self.dsp_power_supply_pin.value = True

    def dsp_button_hold(self, duration: float) -> None:
        self.dsp_button_pin.value = False
        time.sleep(duration)
        self.dsp_button_pin.value = True

    def init_I2C(self) -> None:
        self.i2c = I2C(RPiBoard.PIN_I2C_SCL, RPiBoard.PIN_I2C_SDA)

    def inactivate_ISCP_pins(self) -> None:
        self.dsp_pgd_pin = DigitalInOut(RPiBoard.PIN_DSP_PGD)
        self.dsp_pgd_pin.direction = Direction.OUTPUT
        self.dsp_pgd_pin.value = False

        self.dsp_pgc_pin = DigitalInOut(RPiBoard.PIN_DSP_PGC)
        self.dsp_pgc_pin.direction = Direction.OUTPUT
        self.dsp_pgc_pin.value = False

        # self.dsp_pgd_pin = DigitalInOut(RPiBoard.PIN_DSP_PGD)
        # self.dsp_pgd_pin.direction = Direction.INPUT
        #
        # self.dsp_pgc_pin = DigitalInOut(RPiBoard.PIN_DSP_PGC)
        # self.dsp_pgc_pin.direction = Direction.INPUT

    def deinit_I2C(self) -> None:
        self.i2c.deinit()
        self.i2c = None
        i2c_scl_pin = DigitalInOut(RPiBoard.PIN_I2C_SCL)
        i2c_scl_pin.direction = Direction.INPUT
        i2c_sda_pin = DigitalInOut(RPiBoard.PIN_I2C_SCL)
        i2c_sda_pin.direction = Direction.INPUT


def test():
    b = RPiBoard()
    while True:
        b.dsp_power_supply_pin.value = False
        b.dsp_button_pin.value = False
        print("ON")
        time.sleep(1)
        b.dsp_power_supply_pin.value = False
        b.dsp_button_pin.value = False
        print("OFF")
        time.sleep(1)


def test2():
    b = RPiBoard()
    b.dsp_button_pin.value = False
    time.sleep(1)
    b.dsp_button_pin.value = True


if __name__ == "__main__":
    test2()
