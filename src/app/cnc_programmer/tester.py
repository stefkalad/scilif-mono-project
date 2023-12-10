import logging
import time

from app.cnc_programmer.cnc_programmer_adc import CNCProgrammerADC
from app.cnc_programmer.config.firmware import FirmwareConfig
from app.cnc_programmer.dps_log import DPSLog
from app.cnc_programmer.dps_mode import DPSMode, DPSFlashMode, DPSMaxOnlyMode, FirmwareType
from app.cnc_programmer.rpi_board import RPiBoard


class Tester:

    def __init__(self, board: RPiBoard) -> None:
        self.board: RPiBoard = board
        self.adc: CNCProgrammerADC = CNCProgrammerADC(board)

        self.dps_under_test_mode: DPSMode = None


    def prepare_dps(self) -> None:
        # set offset of ADC for ACS723 (inactivate ISCP pins to do so)
        self.board.inactivate_ISCP_pins()
        self.set_LED_current_offset()
        # turn on power supply of DPS
        self.board.dps_activate()


    def test_dps_flash(self, config: FirmwareConfig, dps_log: DPSLog) -> None:
        self.dps_under_test_mode = DPSFlashMode.STRONG
        # wait until stable
        time.sleep(0.5)
        # measure button LED voltage (in the strong lighting mode)
        button_led_voltage_passed, button_led_voltage = self.test_button_LED_voltage(config)
        # measure r_feedback voltage (in the strong lighting mode)
        r_feedback_voltage_passed, r_feedback_voltage = self.test_r_feedback_voltage(config)
        # measure current in the strong lighting mode
        led_current_strong_mode_passed, led_current_strong_mode = self.test_LED_current(config, FirmwareType.FLASH, self.dps_under_test_mode)
        # increase the lighting mode
        self.increase_dps_under_test_mode(config)
        # wait until stable
        time.sleep(0.5)
        # measure current in the low lighting mode
        led_current_light_mode_passed, led_current_light_mode = self.test_LED_current(config, FirmwareType.FLASH, self.dps_under_test_mode)
        # turn off DPS power supply
        self.board.dps_inactivate()

        # set DPS log
        dps_log.led_current_mode1_passed = led_current_strong_mode_passed
        dps_log.led_current_mode1 = led_current_strong_mode
        dps_log.led_current_mode2_passed = led_current_light_mode_passed
        dps_log.led_current_mode2 = led_current_light_mode
        dps_log.button_led_voltage_passed = button_led_voltage_passed
        dps_log.button_led_voltage = button_led_voltage
        dps_log.r_feedback_voltage_passed = r_feedback_voltage_passed
        dps_log.r_feedback_voltage = r_feedback_voltage

    def test_dps_maxonly(self, config: FirmwareConfig, dps_log: DPSLog) -> None:
        self.dps_under_test_mode = DPSMaxOnlyMode.NO
        # wait until stable
        time.sleep(0.5)
        # increase the lighting mode
        self.increase_dps_under_test_mode(config)
        # wait until stable
        time.sleep(0.5)
        # measure button LED voltage
        button_led_voltage_passed, button_led_voltage = self.test_button_LED_voltage(config)
        # measure r_feedback voltage
        r_feedback_voltage_passed, r_feedback_voltage = self.test_r_feedback_voltage(config)
        # measure current in the low lighting mode
        led_current_strong_mode_passed, led_current_strong_mode = self.test_LED_current(config, FirmwareType.MAX_ONLY, self.dps_under_test_mode)
        # turn off DPS power supply
        self.board.dps_inactivate()

        # set DPS log
        dps_log.led_current_mode1_passed = led_current_strong_mode_passed
        dps_log.led_current_mode1 = led_current_strong_mode
        dps_log.button_led_voltage_passed = button_led_voltage_passed
        dps_log.button_led_voltage = button_led_voltage
        dps_log.r_feedback_voltage_passed = r_feedback_voltage_passed
        dps_log.r_feedback_voltage = r_feedback_voltage



    def increase_dps_under_test_mode(self, config: FirmwareConfig) -> None:
        self.dps_under_test_mode = self.dps_under_test_mode.__class__.increase_mode(self.dps_under_test_mode)
        self.board.dps_button_hold(config.button_led_mode_change_duration / 1000)


    def set_LED_current_offset(self) -> None:
        voltage_offset: float = self.adc.measure_voltage_on_acs723_mV()
        logging.info(f"ADC ACS723 voltage offset set to {voltage_offset} mV")
        self.adc.acs723_voltage_offset_mV = voltage_offset

    def test_LED_current(self, config: FirmwareConfig, firmware_type: FirmwareType, mode: DPSMode) -> (bool, float):
        led_current: float = self.adc.measure_led_current_on_acs723_mA()
        test_passed: bool = self._check_in_range(led_current, self._get_allowed_led_current_range(config, firmware_type, mode))
        logging.info(f"Measured LED current in mode: {mode.value}, current {led_current} mA, test passed: {test_passed}")
        return test_passed, led_current

    def test_button_LED_voltage(self, config: FirmwareConfig) -> (bool, float):
        button_led_voltage = self.adc.measure_voltage_on_button_led_mV()
        test_passed: bool = self._check_in_range(button_led_voltage, config.button_led_voltage)
        return True, test_passed, button_led_voltage

    def test_r_feedback_voltage(self, config: FirmwareConfig) -> (bool, float):
        r_feedback_voltage = self.adc.measure_voltage_on_feedback_resistor_mV()
        test_passed: bool = self._check_in_range(r_feedback_voltage, config.r_feedback_voltage)
        return True, test_passed, r_feedback_voltage

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
