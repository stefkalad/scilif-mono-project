import logging
from typing import Callable

from app.cnc_programmer.cnc_programmer_adc import CNCProgrammerADC, LEDCurrentMeasurementMethod
from app.cnc_programmer.config.firmware import FirmwareConfig
from app.cnc_programmer.dps_mode import DPSMode, DPSFlashMode, DPSMaxOnlyMode, FirmwareType
from app.cnc_programmer.rpi_board import RPiBoard


class Tester:

    def __init__(self, board: RPiBoard) -> None:
        self.board: RPiBoard = board
        self.adc: CNCProgrammerADC = CNCProgrammerADC(board)

    def set_LED_current_offset(self) -> None:
        voltage_offset: float = self.adc.measure_voltage_on_acs723_mV()
        logging.info(f"ADC ACS723 voltage offset set to {voltage_offset} mV")
        self.adc.acs723_voltage_offset_mV = voltage_offset

    def measure_LED_current(self, method: LEDCurrentMeasurementMethod = LEDCurrentMeasurementMethod.ACS723) -> float:
        return self._get_LED_current_measurement_method(method)()

    def test_LED_current(self, config: FirmwareConfig, firmware_type: FirmwareType, mode: DPSMode, method: LEDCurrentMeasurementMethod = LEDCurrentMeasurementMethod.ACS723) -> (bool, float):
        led_current: float = self.measure_LED_current(method)
        test_passed: bool = self._check_in_range(led_current, self._get_allowed_led_current_range(config, firmware_type, mode))
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

    def _get_allowed_led_current_range(self, config: FirmwareConfig, firmware_type: FirmwareType, mode: DPSMode):
        if firmware_type == FirmwareType.MAX_ONLY:
            if mode == DPSMaxOnlyMode.STRONG:
                return config.led_current_mode1
        elif firmware_type == FirmwareType.FLASH:
            if mode == DPSFlashMode.STRONG:
                return config.led_current_mode1
            if mode == DPSFlashMode.LIGHT:
                return config.led_current_mode2
        raise Exception("Blinking mode does not have an allowed range!")

    def _check_in_range(self, value: float, allowed_range: (float, float)) -> bool:
        return allowed_range[0] <= value <= allowed_range[1]
