import time
from enum import Enum

import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

from app.cnc_programmer.rpi_board import RPiBoard
from lib.adc import ADC, GAIN


class LEDCurrentMeasurementMethod(Enum):
    SHUNT = 0
    ACS723 = 1


class CNCProgrammerADC(ADC):
    SAMPLES_TO_AVERAGE: int = 5

    SHUNT_RESISTENCE: int = 10

    ACS723_VOLTAGE_TO_CURRENT_RATIO: float = 1 / 0.4
    DEFAULT_ACS723_VOLTAGE_OFFSET_MV: float = 167

    LED_SHUNT_CHANNEL_0: int = ADS.P0
    LED_SHUNT_CHANNEL_1: int = ADS.P1

    ACS723_OUTPUT_CHANNEL: int = ADS.P0
    REFERENCE_CHANNEL: int = ADS.P1
    R_FEEDBACK_CHANNEL: int = ADS.P2
    BUTTON_LED_CHANNEL: int = ADS.P3

    def __init__(self, board: RPiBoard) -> None:
        super().__init__(board)

        self.channel_acs723_D: AnalogIn = AnalogIn(self.adc, CNCProgrammerADC.ACS723_OUTPUT_CHANNEL, CNCProgrammerADC.REFERENCE_CHANNEL)
        # self.channel_acs723: AnalogIn = AnalogIn(self.adc, ADC.ACS723_OUTPUT_CHANNEL)
        self.channel_button_led: AnalogIn = AnalogIn(self.adc, CNCProgrammerADC.BUTTON_LED_CHANNEL)
        self.channel_feedback_resistor: AnalogIn = AnalogIn(self.adc, CNCProgrammerADC.R_FEEDBACK_CHANNEL)
        self.channel_vdd: AnalogIn = AnalogIn(self.adc, CNCProgrammerADC.REFERENCE_CHANNEL)

        # NOTE: note used
        self.channel_shunt_0: AnalogIn = AnalogIn(self.adc, CNCProgrammerADC.LED_SHUNT_CHANNEL_0)
        self.channel_shunt_1: AnalogIn = AnalogIn(self.adc, CNCProgrammerADC.LED_SHUNT_CHANNEL_1)

        # self.channel_acs723: AnalogIn = AnalogIn(self.adc, ADC.ACS723_OUTPUT_CHANNEL)
        # self.channel_ref2: AnalogIn = AnalogIn(self.adc, ADC.REFERENCE_CHANNEL)
        self.acs723_voltage_offset_mV: float = CNCProgrammerADC.DEFAULT_ACS723_VOLTAGE_OFFSET_MV

    def measure_voltage_on_shunt_mV(self) -> float | None:
        if self.adc is None: return None

        self.set_adc_gain(GAIN.GAIN_1.value)
        time.sleep(0.01)
        chan0_voltage: float = self.measure_N_times(CNCProgrammerADC.SAMPLES_TO_AVERAGE, self.channel_shunt_0)
        self.set_adc_gain(GAIN.GAIN_4.value)
        time.sleep(0.01)
        chan1_voltage: float = self.measure_N_times(CNCProgrammerADC.SAMPLES_TO_AVERAGE, self.channel_shunt_1)
        return (chan0_voltage - chan1_voltage) * 1000

    def measure_led_current_on_shunt_mA(self) -> float | None:
        if self.adc is None: return None

        return self.measure_voltage_on_shunt_mV() / CNCProgrammerADC.SHUNT_RESISTENCE

    def measure_voltage_on_acs723_mV(self) -> float | None:
        if self.adc is None: return None

        self.set_adc_gain(GAIN.GAIN_8.value)
        time.sleep(0.01)
        chan01_D_voltage: float = self.measure_N_times(CNCProgrammerADC.SAMPLES_TO_AVERAGE, self.channel_acs723_D)
        # self.set_adc_gain(GAIN.GAIN_23.value)
        # chan3_voltage: float = self.measure_N_times(ADC.SAMPLES_TO_AVERAGE, self.channel_vdd)
        # time.sleep(0.01)
        return chan01_D_voltage * 1000

        # self.set_adc_gain(GAIN.GAIN_1.value)
        # time.sleep(0.01)
        # chan2_voltage: float = self.measure_N_times(ADC.SAMPLES_TO_AVERAGE, self.channel_acs723)
        # print(chan2_voltage)
        # chan3_voltage: float = self.measure_N_times(ADC.SAMPLES_TO_AVERAGE, self.channel_ref2)
        # print(chan3_voltage)
        #
        # return (chan2_voltage - chan3_voltage) * 1000

    def measure_led_current_on_acs723_mA(self) -> float | None:
        if self.adc is None: return None

        return (self.measure_voltage_on_acs723_mV() - self.acs723_voltage_offset_mV) * CNCProgrammerADC.ACS723_VOLTAGE_TO_CURRENT_RATIO  # 2.5 A/V = 2500 mA/V

    def measure_voltage_on_feedback_resistor_mV(self) -> float | None:
        if self.adc is None: return None

        self.set_adc_gain(GAIN.GAIN_8.value)
        time.sleep(0.01)
        chan1_voltage: float = self.measure_N_times(CNCProgrammerADC.SAMPLES_TO_AVERAGE, self.channel_feedback_resistor)
        return chan1_voltage * 1000

    def measure_voltage_on_button_led_mV(self) -> float | None:
        if self.adc is None: return None

        self.set_adc_gain(GAIN.GAIN_23.value)
        time.sleep(0.01)
        chan0_voltage: float = self.measure_N_times(CNCProgrammerADC.SAMPLES_TO_AVERAGE, self.channel_button_led)
        return chan0_voltage * 1000

def test2():

    board = RPiBoard()
    adc = CNCProgrammerADC(board)
    # shut down
    board.dps_power_supply_pin.value = True
    time.sleep(1)
    # offset
    offset_acs723 = adc.measure_voltage_on_acs723_mV()
    print(f"ACS723 Offset: {offset_acs723:2f} mV")
    adc.acs723_voltage_offset_mV = offset_acs723
    # power up
    board.dps_power_supply_pin.value = False
    time.sleep(1)

    print("{:>6}\t\t{:>6}\t\t{:>6}\t\t{:>6}".format('LED [mV]', 'R_FB [mV]', 'ACS723 [mV]', 'ACS723 [mA]'))

    while True:
        voltage_button_led = adc.measure_voltage_on_button_led_mV()
        voltage_feedback_resistor = adc.measure_voltage_on_feedback_resistor_mV()
        voltage_acs723 = adc.measure_voltage_on_acs723_mV()
        current_acs723 = adc.measure_led_current_on_acs723_mA()

        print("{:>5.3f}\t\t{:>5.3f}\t\t{:>5.3f}\t\t{:>5.3f}".format(voltage_button_led, voltage_feedback_resistor, voltage_acs723, current_acs723))
        time.sleep(0.5)


if __name__ == "__main__":
    test2()