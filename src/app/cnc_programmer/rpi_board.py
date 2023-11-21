import time

import board
from busio import I2C
from digitalio import Direction, DigitalInOut, Pull


class RPiBoard:
    PIN_I2C_SCL = board.SCL
    PIN_I2C_SDA = board.SDA

    PIN_DPS_VPP = board.D17
    PIN_DPS_PGD = board.D22
    PIN_DPS_PGC = board.D27

    PIN_DPS_BUTTON = board.D18
    PIN_DPS_POWER_SUPPLY = board.D23

    # Pin Definitions
    PIN_STEPPER_X_STEP = board.D20
    PIN_STEPPER_X_DIR = board.D21  # Output 0 -> X goes left
    PIN_STEPPER_Y_STEP = board.D5
    PIN_STEPPER_Y_DIR = board.D6  # Output 0 -> Y goes positive (from operator)
    PIN_STEPPER_Z_STEP = board.D13
    PIN_STEPPER_Z_DIR = board.D19   # Output 0 -> Z goes up

    PIN_STEPPER_CONTACT = board.D24

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

        self.stepper_contacting_pin = DigitalInOut(RPiBoard.PIN_STEPPER_CONTACT)
        self.stepper_contacting_pin.direction = Direction.INPUT
        self.stepper_contacting_pin.pull = Pull.DOWN

        # DPS power supply
        self.dps_power_supply_pin = DigitalInOut(RPiBoard.PIN_DPS_POWER_SUPPLY)
        self.dps_power_supply_pin.direction = Direction.OUTPUT

        # DPS button
        self.dps_button_pin = DigitalInOut(RPiBoard.PIN_DPS_BUTTON)
        self.dps_button_pin.direction = Direction.OUTPUT

        # DPS ICSP programmer
        self.dps_vpp_pin = None
        self.dps_pgd_pin = None
        self.dps_pgc_pin = None

        # Note: set button to HIGH to prevent click emulation
        self.dps_button_pin.value = True
        # Note: set power supply pon to HIGH to not activate DPS
        self.dps_power_supply_pin.value = True

    def deinit(self) -> None:
        self.set_stepper_pins_on_destroy()

    def set_stepper_pins_on_destroy(self) -> None:
        for pin in self.stepper_dir_pins + self.stepper_step_pins:
            pin.direction = Direction.OUTPUT
            pin.value = False

    def dps_activate(self) -> None:
        self.dps_power_supply_pin.value = False

    def dps_inactivate(self) -> None:
        self.dps_power_supply_pin.value = True

    def dps_button_hold(self, duration: float) -> None:
        self.dps_button_pin.value = False
        time.sleep(duration)
        self.dps_button_pin.value = True

    def init_I2C(self) -> None:
        self.i2c = I2C(RPiBoard.PIN_I2C_SCL, RPiBoard.PIN_I2C_SDA)

    def inactivate_ISCP_pins(self) -> None:
        self.dps_pgd_pin = DigitalInOut(RPiBoard.PIN_DPS_PGD)
        self.dps_pgd_pin.direction = Direction.OUTPUT
        self.dps_pgd_pin.value = False

        self.dps_pgc_pin = DigitalInOut(RPiBoard.PIN_DPS_PGC)
        self.dps_pgc_pin.direction = Direction.OUTPUT
        self.dps_pgc_pin.value = False

        # self.dps_pgd_pin = DigitalInOut(RPiBoard.PIN_DPS_PGD)
        # self.dps_pgd_pin.direction = Direction.INPUT
        #
        # self.dps_pgc_pin = DigitalInOut(RPiBoard.PIN_DPS_PGC)
        # self.dps_pgc_pin.direction = Direction.INPUT

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
        b.dps_power_supply_pin.value = False
        b.dps_button_pin.value = False
        print("ON")
        time.sleep(1)
        b.dps_power_supply_pin.value = True
        b.dps_button_pin.value = True
        print("OFF")
        time.sleep(1)

def test_vpp():
    print("Test VPP/PGC/VDD")
    b = RPiBoard()
    b.dps_power_supply_pin.value = False
    vpp = DigitalInOut(RPiBoard.PIN_DPS_VPP)
    vpp.direction = Direction.OUTPUT

    pgc = DigitalInOut(RPiBoard.PIN_DPS_PGC)
    pgc.direction = Direction.OUTPUT

    pgd = DigitalInOut(RPiBoard.PIN_DPS_PGD)
    pgd.direction = Direction.OUTPUT

    while True:
        b.dps_power_supply_pin.value = False
        vpp.value = True
        pgc.value = True
        pgd.value = True
        time.sleep(0.1)
        vpp.value = False
        pgc.value = False
        pgd.value = False
        b.dps_power_supply_pin.value = True
        time.sleep(0.1)

def test_contacting():
    print("Contacting Test")

    board = RPiBoard()
    while True:
        print(board.stepper_contacting_pin.value)
        time.sleep(1)



if __name__ == "__main__":
    test_contacting()
    # test_vpp()
