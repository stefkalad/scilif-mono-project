import time
from typing import Callable

import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from enum import Enum

from app.cnc_programmer.rpi_board import RPiBoard


#       GAIN    RANGE (V)
#       ----    ---------
#        2/3    +/- 6.144
#          1    +/- 4.096
#          2    +/- 2.048
#          4    +/- 1.024
#          8    +/- 0.512
#         16    +/- 0.256

class GAIN(Enum):
    GAIN_23 = 2 / 3
    GAIN_1 = 1
    GAIN_2 = 2
    GAIN_4 = 4
    GAIN_8 = 8
    GAIN_16 = 16

class LEDCurrentMeasurementMethod(Enum):
    SHUNT = 0
    ACS723 = 1


class ADC:
    SAMPLES_TO_AVERAGE: int = 5

    SHUNT_RESISTENCE: int = 10

    ACS723_VOLTAGE_TO_CURRENT_RATIO: float = 1 / 0.4
    ACS723_VOLTAGE_OFFSET: float = 0.0132

    LED_SHUNT_CHANNEL_0: int = ADS.P0
    LED_SHUNT_CHANNEL_1: int = ADS.P1
    ACS723_OUTPUT_CHANNEL: int = ADS.P2
    REFERENCE_CHANNEL: int = ADS.P3

    def __init__(self, board: RPiBoard) -> None:
        self.board = board
        self.adc = ADS.ADS1115(self.board.i2c)
        self.channel_shunt_0: AnalogIn = AnalogIn(self.adc, ADC.LED_SHUNT_CHANNEL_0)
        self.channel_shunt_1: AnalogIn = AnalogIn(self.adc, ADC.LED_SHUNT_CHANNEL_1)
        self.channel_acs723_D: AnalogIn = AnalogIn(self.adc, ADC.ACS723_OUTPUT_CHANNEL, ADC.REFERENCE_CHANNEL)

    def measure_voltage_on_shunt_mV(self) -> float:
        self.set_adc_gain(GAIN.GAIN_1.value)
        time.sleep(0.01)
        chan0_voltage: float = self.measure_N_times(ADC.SAMPLES_TO_AVERAGE, self.channel_shunt_0)
        self.set_adc_gain(GAIN.GAIN_4.value)
        time.sleep(0.01)
        chan1_voltage: float = self.measure_N_times(ADC.SAMPLES_TO_AVERAGE, self.channel_shunt_1)
        return (chan0_voltage - chan1_voltage) * 1000

    # def measure_voltage_on_shunt_mV(self) -> float:
    #     self.set_adc_gain(GAIN.GAIN_1.value)
    #     chan0_voltage: float = self.measure_N_times(ADC.SAMPLES_TO_AVERAGE,
    #                                                 lambda: AnalogIn(self.adc, ADC.LED_SHUNT_CHANNEL_0))
    #     self.set_adc_gain(GAIN.GAIN_4.value)
    #     chan1_voltage: float = self.measure_N_times(ADC.SAMPLES_TO_AVERAGE,
    #                                                 lambda: AnalogIn(self.adc, ADC.LED_SHUNT_CHANNEL_1))
    #     return (chan0_voltage - chan1_voltage) * 1000

    def measure_led_current_on_shunt_mA(self) -> float:
        return self.measure_voltage_on_shunt_mV() / ADC.SHUNT_RESISTENCE

    def measure_voltage_on_acs723_mV(self) -> float:
        self.set_adc_gain(GAIN.GAIN_16.value)
        time.sleep(0.01)
        chan23_D_voltage: float = self.measure_N_times(ADC.SAMPLES_TO_AVERAGE, self.channel_acs723_D)
        return chan23_D_voltage * 1000

    # def measure_voltage_on_acs723_mV(self) -> float:
    #     self.set_adc_gain(GAIN.GAIN_16.value)
    #     chan23_D_voltage: float = self.measure_N_times(ADC.SAMPLES_TO_AVERAGE,
    #                                                    lambda: AnalogIn(self.adc, ADC.ACS723_OUTPUT_CHANNEL, ADC.REFERENCE_CHANNEL))
    #     return chan23_D_voltage * 1000

    def measure_led_current_on_acs723_mA(self) -> float:
        return (self.measure_voltage_on_acs723_mV() - ADC.ACS723_VOLTAGE_OFFSET * 1000) * ADC.ACS723_VOLTAGE_TO_CURRENT_RATIO  # 2.5 A/V = 2500 mA/V

    def set_adc_gain(self, gain) -> None:
        self.adc.gain = gain

    def measure_N_times(self, N: int, channel: AnalogIn) -> float:
        total: float = 0
        for i in range(N):
            total += channel.voltage
            time.sleep(0.01)
        return total / N

    # def measure_N_times(self, N: int, measure_func: Callable[[], AnalogIn]) -> float:
    #     total: float = 0
    #     for i in range(N):
    #         channel: AnalogIn = measure_func()
    #         total += channel.voltage
    #         time.sleep(0.01)
    #     return total / N


def test():
    print("{:>6}\t\t{:>6}\t\t{:>6}\t\t{:>6}".format('SHUNT [mV]', 'SHUNT [mA]', 'ACS723 [mV]', 'ACS723 [mA]'))

    board = RPiBoard()
    board.dsp_power_supply_pin.value = False
    adc = ADC(board)

    while True:
        voltage_shunt = adc.measure_voltage_on_shunt_mV()
        current_shunt = adc.measure_led_current_on_shunt_mA()

        voltage_acs723 = adc.measure_voltage_on_acs723_mV()
        current_acs723 = adc.measure_led_current_on_acs723_mA()

        print("{:>5.3f}\t\t{:>5.3f}\t\t{:>5.3f}\t\t{:>5.3f}".format(voltage_shunt, current_shunt, voltage_acs723, current_acs723))
        # print("{:>5.3f}\t\t{:>5.3f}\t\t{:>5.3f}\t\t{:>5.3f}".format(, chan23_D_voltage * 1000, chan23_D_current, chan3.voltage * 1000))
        time.sleep(0.5)


if __name__ == "__main__":
    test()
