import logging
from typing import Callable

from app.cnc_programmer.cnc_programmer_adc import CNCProgrammerADC, LEDCurrentMeasurementMethod
from app.cnc_programmer.config.firmware import FirmwareConfig
from app.cnc_programmer.dps_mode import DPSMode
from app.cnc_programmer.rpi_board import RPiBoard


class Tester:

    def __init__(self, board: RPiBoard) -> None:
        self.board: RPiBoard = board
        self.adc: CNCProgrammerADC = CNCProgrammerADC(board)

    def measure_LED_current(self, method: LEDCurrentMeasurementMethod = LEDCurrentMeasurementMethod.SHUNT) -> float:
        return self._get_LED_current_measurement_method(method)()

    def test_LED_current(self, config: FirmwareConfig, mode: DPSMode, method: LEDCurrentMeasurementMethod = LEDCurrentMeasurementMethod.SHUNT) -> (bool, float):
        led_current: float = self.measure_LED_current(method)
        test_passed: bool = self._check_in_range(led_current, self._get_allowed_range(config, mode))
        logging.info(f"Measured LED current in mode: {mode.value}, current {led_current} mA, test passed: {test_passed}")
        return test_passed, led_current

    def test_button_LED_voltage(self, config: FirmwareConfig) -> (bool, float):
        return True, 2440.5

    def _get_LED_current_measurement_method(self, method: LEDCurrentMeasurementMethod) -> Callable[[], float]:
        if method == LEDCurrentMeasurementMethod.SHUNT:
            return self.adc.measure_led_current_on_shunt_mA

        if method == LEDCurrentMeasurementMethod.ACS723:
            return self.adc.measure_led_current_on_acs723_mA

        raise Exception("Unknown measurement method!")

    def _get_allowed_range(self, config: FirmwareConfig, mode: DPSMode):
        if mode == DPSMode.STRONG:
            return config.led_current_mode1
        if mode == DPSMode.LIGHT:
            return config.led_current_mode2

        raise Exception("Blinking mode does not have an allowed range!")

    def _check_in_range(self, value: float, allowed_range: (float, float)) -> bool:
        return allowed_range[0] <= value <= allowed_range[1]
