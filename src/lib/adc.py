import logging
import time

import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from enum import Enum


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


class ADC:
    def __init__(self, board) -> None:
        self.board = board
        try:
            self.adc = ADS.ADS1115(self.board.i2c)
        except ValueError:
            logging.error("ADC initialization failure, I2C cannot read address from ADC")
            self.adc = None
            return

    def set_adc_gain(self, gain) -> None:
        self.adc.gain = gain

    def measure_N_times(self, N: int, channel: AnalogIn) -> float:
        total: float = 0
        for i in range(N):
            total += channel.voltage
            time.sleep(0.01)
        return total / N

