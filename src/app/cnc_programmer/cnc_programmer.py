import time
import os

from app.cnc_programmer.dsp_programmer import DspProgrammer
from app.cnc_programmer.rpi_board import RPiBoard
from app.cnc_programmer.dsp_mode import DSPMode
from app.cnc_programmer.tester import Tester
from lib.adc import LEDCurrentMeasurementMethod
from lib.config_parser import CNCProgrammerConfig


class CNCProgrammer:

    def __init__(self, config: CNCProgrammerConfig) -> None:
        self.config = config

        self.board = RPiBoard()
        self.programmer = DspProgrammer()
        self.tester = Tester(config, self.board)
        self.dsp_mode = None
        print("CNC programmer running...")

    def process_dsp(self) -> bool:
        # turn on power supply of DSP
        self.activate_dsp()

        # program firmware
        self.programmer.load()
        # deinit ISCP pins
        self.board.inactivate_ISCP_pins()
        # wait until stable TODO: is it needed?
        time.sleep(2)
        # measure current in the strong lightig mode
        self.dsp_mode = DSPMode.STRONG
        test_led_current_strong_mode_passed: bool = self.tester.test_LED_current(self.dsp_mode)

        # increase the lighting mode
        self.increase_dsp_mode()
        # wait until stable TODO: is it needed?
        time.sleep(2)
        # measure current in the low lighting mode
        test_led_current_light_mode_passed: bool = self.tester.test_LED_current(self.dsp_mode)
        # turn off DSP power supply
        self.inactivate_dsp()

        print(f"Test strong mode: {test_led_current_strong_mode_passed}, light mode: {test_led_current_light_mode_passed}")
        return test_led_current_strong_mode_passed and test_led_current_light_mode_passed


    def activate_dsp(self) -> None:
        self.board.dsp_power_supply_pin.value = False

    def inactivate_dsp(self) -> None:
        self.board.dsp_power_supply_pin.value = True

    def increase_dsp_mode(self) -> None:
        self.dsp_mode = DSPMode.increase_mode(self.dsp_mode)
        self.hold_button()

    def hold_button(self) -> None:
        print("Button hold")
        self.board.dsp_button_pin.value = False
        time.sleep(self.config.button_led_mode_change_duration/1000)
        print("Button released")
        self.board.dsp_button_pin.value = True









