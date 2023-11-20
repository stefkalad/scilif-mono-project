import time

import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from enum import Enum

from app.final_tester.rpi_board import RPiBoard
from lib.adc import ADC, GAIN


class FinalTesterADC(ADC):
    SAMPLES_TO_AVERAGE: int = 5

    SHUNT_RESISTENCE: int = 0.1

    ACS723_VOLTAGE_TO_CURRENT_RATIO: float = 1 / 0.4
    DEFAULT_ACS723_VOLTAGE_OFFSET_MV: float = 167

    USB_SHUNT_CHANNEL_0: int = ADS.P0
    USB_SHUNT_CHANNEL_1: int = ADS.P1

    L_PHOTODIODE_CHANNEL: int = ADS.P0
    R_PHOTODIODE_CHANNEL: int = ADS.P1


    def __init__(self, board: RPiBoard) -> None:
        super().__init__(board)

        # NOTE: note used
        self.channel_usb_shunt_D: AnalogIn = AnalogIn(self.adc, FinalTesterADC.USB_SHUNT_CHANNEL_0, FinalTesterADC.USB_SHUNT_CHANNEL_1)
        self.channel_l_photodiode: AnalogIn = AnalogIn(self.adc, FinalTesterADC.L_PHOTODIODE_CHANNEL)
        self.channel_r_photodiode: AnalogIn = AnalogIn(self.adc, FinalTesterADC.R_PHOTODIODE_CHANNEL)


    def measure_voltage_on_usb_shunt_mV(self) -> float | None:
        if self.adc is None: return None

        self.set_adc_gain(GAIN.GAIN_4.value)
        time.sleep(0.01)
        chan01_D_voltage: float = self.measure_N_times(FinalTesterADC.SAMPLES_TO_AVERAGE, self.channel_usb_shunt_D)
        return chan01_D_voltage * 1000

    def measure_current_on_usb_shunt_mA(self) -> float | None:
        if self.adc is None: return None

        return self.measure_voltage_on_usb_shunt_mV() / FinalTesterADC.SHUNT_RESISTENCE


    def measure_voltage_on_photodiode_mV(self, diode='L') -> float | None:
        if self.adc is None: return None

        self.set_adc_gain(GAIN.GAIN_1.value)
        time.sleep(0.01)
        if diode == 'L':
            chan_diode_voltage: float = self.measure_N_times(FinalTesterADC.SAMPLES_TO_AVERAGE, self.channel_l_photodiode)
        elif diode == 'R':
            chan_diode_voltage: float = self.measure_N_times(FinalTesterADC.SAMPLES_TO_AVERAGE, self.channel_r_photodiode)
        else:
            raise Exception(f"Wrong input parameter diode= {diode}")

        return chan_diode_voltage * 1000


def test():

    board = RPiBoard()
    adc = FinalTesterADC(board)

    print("{:>6}\t\t{:>6}\t\t{:>6}\t\t{:>6}".format('USB [mV]', 'USB [mA]', 'L PHOTO [mV]', 'R PHOTO [mB]'))

    while True:
        voltage_shunt = adc.measure_voltage_on_usb_shunt_mV()
        current_shunt = adc.measure_current_on_usb_shunt_mA()
        voltage_l_photo = adc.measure_voltage_on_photodiode_mV('L')
        voltage_r_photo = adc.measure_voltage_on_photodiode_mV('R')

        print("{:>5.3f}\t\t{:>5.3f}\t\t{:>5.3f}\t\t{:>5.3f}".format(voltage_shunt, current_shunt,voltage_l_photo, voltage_r_photo))
        time.sleep(0.5)


if __name__ == "__main__":
    test()