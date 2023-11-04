import time
import numpy as np


from app.cnc_programmer.dsp_programmer import DSProgrammer
from app.cnc_programmer.rpi_board import RPiBoard
from app.cnc_programmer.dsp_mode import DSPMode
from app.cnc_programmer.stepper.position import Axis
from app.cnc_programmer.stepper.stepper_driver import StepperDriver
from app.cnc_programmer.tester import Tester
from lib.adc import LEDCurrentMeasurementMethod
from lib.config_parser import CNCProgrammerConfig


#TODO: GUI
#TODO: Z Axis
#TODO:

#TODO: logging
#TODO: RUN as process

class CNCProgrammer:

    def __init__(self, config: CNCProgrammerConfig) -> None:
        self.config = config

        self.board = RPiBoard()
        self.stepper_driver = StepperDriver(self.board)
        self.programmer = DSProgrammer()
        self.tester = Tester(config, self.board)

        self.dsp_under_test_mode = None

        print("CNC Programmer was successfully initialized...")

    def process_dsp(self) -> bool:
        # turn on power supply of DSP
        self.board.dsp_activate()

        # program firmware
        self.programmer.load()
        # deinit ISCP pins
        self.board.inactivate_ISCP_pins()
        # wait until stable TODO: is it needed?
        time.sleep(2)
        # measure current in the strong lightig mode
        self.dsp_under_test_mode = DSPMode.STRONG
        test_led_current_strong_mode_passed: bool = self.tester.test_LED_current(self.dsp_under_test_mode)

        # increase the lighting mode
        self.increase_dsp_under_test_mode()
        # wait until stable TODO: is it needed?
        time.sleep(2)
        # measure current in the low lighting mode
        test_led_current_light_mode_passed: bool = self.tester.test_LED_current(self.dsp_under_test_mode)
        # turn off DSP power supply
        self.board.dsp_inactivate()

        print(f"Test strong mode: {test_led_current_strong_mode_passed}, light mode: {test_led_current_light_mode_passed}")
        return test_led_current_strong_mode_passed and test_led_current_light_mode_passed

    def increase_dsp_under_test_mode(self) -> None:
        self.dsp_under_test_mode = DSPMode.increase_mode(self.dsp_under_test_mode)
        self.board.dsp_button_hold(self.config.button_led_mode_change_duration/1000)

    def _generate_x_coordinate_sequence(self, rows: int, columns: int) -> np.array:
        return np.repeat(np.arange(rows), columns)

    def _generate_y_coordinate_sequence(self, rows: int, columns: int) -> np.array:
        return np.repeat(np.arange(rows), columns)


    def start_programming_dsp_plate(self) -> None:

        for row in range(self.config.plate_rows):
            for column in range(self.config.plate_columns):
                # if the row is even ---> increase column, if odd <--- decrease column
                column = column if row % 2 == 0 else self.config.plate_columns - column - 1
                print(f"[{column}, {row}]")
                pos_target_x_mm: float = (column + 1/2) * self.config.dsp_width + self.config.plate_x_offset
                pos_target_y_mm: float = (row + 1/2) * self.config.dsp_width + self.config.plate_x_offset
                self.stepper_driver.go(Axis.X, pos_target_x_mm, 100)
                self.stepper_driver.go(Axis.Y, pos_target_y_mm, 100)
                #TODO: go Z

                self.process_dsp()



def test():
    config = CNCProgrammerConfig(f"./resources/config_cnc_programmer.conf", "firmware_thule_two_modes", "plate_thule_4332")
    print(config)
    programmer = CNCProgrammer(config)
    programmer.start_programming_dsp_plate()


if __name__ == "__main__":
    test()











