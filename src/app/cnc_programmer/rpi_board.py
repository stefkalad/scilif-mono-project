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

    def __init__(self) -> None:
        self.init_I2C()

        self.dsp_pgd_pin = None
        self.dsp_pgc_pin = None

        self.dsp_power_supply_pin = DigitalInOut(RPiBoard.PIN_DSP_POWER_SUPPLY)
        self.dsp_power_supply_pin.direction = Direction.OUTPUT

        self.dsp_button_pin = DigitalInOut(RPiBoard.PIN_DSP_BUTTON)
        self.dsp_button_pin.direction = Direction.OUTPUT


        # Note: set button to HIGH to prevent click emulation
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
