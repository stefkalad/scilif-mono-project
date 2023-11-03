from typing import Callable

from app.cnc_programmer.dsp_mode import DSPMode
from app.cnc_programmer.rpi_board import RPiBoard
from lib.adc import ADC, LEDCurrentMeasurementMethod
from lib.config_parser import CNCProgrammerConfig


class Tester:

    def __init__(self, config: CNCProgrammerConfig, board: RPiBoard) -> None:
        self.config = config
        self.board = board
        self.adc = ADC(board)

    def measure_LED_current(self, method: LEDCurrentMeasurementMethod = LEDCurrentMeasurementMethod.SHUNT) -> float:
        return self.get_LED_current_measurement_method(method)()

    def test_LED_current(self, mode: DSPMode, method: LEDCurrentMeasurementMethod = LEDCurrentMeasurementMethod.SHUNT) -> bool:
        led_current: float = self.measure_LED_current(method)
        print(f"Mode: {mode.value}, current {led_current} mA")

        return Tester.__check_in_range(led_current, self.get_allowed_range(mode))

    def get_LED_current_measurement_method(self, method: LEDCurrentMeasurementMethod) -> Callable[[], float]:
        if method == LEDCurrentMeasurementMethod.SHUNT:
            return self.adc.measure_led_current_on_shunt_mA

        if method == LEDCurrentMeasurementMethod.ACS723:
            return self.adc.measure_led_current_on_acs723_mA

        raise Exception("Unknown measurement method!")

    def get_allowed_range(self, mode):
        if mode == DSPMode.STRONG:
            return self.config.led_current_mode1
        if mode == DSPMode.LIGHT:
            return self.config.led_current_mode2

        raise Exception("Blinking mode does not have an allowed range!")

    @staticmethod
    def __check_in_range(value: float, allowed_range: (float, float, float)) -> bool:
        return allowed_range[0] <= value <= allowed_range[2]
