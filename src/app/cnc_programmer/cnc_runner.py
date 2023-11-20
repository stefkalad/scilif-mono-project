from __future__ import annotations

import time
import logging
import threading
from subprocess import CompletedProcess

from app.cnc_programmer.config.config import CNCProgrammerConfig
from app.cnc_programmer.config.config_parser import CNCProgrammerConfigParser
from app.cnc_programmer.config.firmware import FirmwareConfig
from app.cnc_programmer.config.plate import PlateConfig
from app.cnc_programmer.dps_log import DPSLog
from app.cnc_programmer.dps_programmer import DPSProgrammer
from app.cnc_programmer.gui.gui import GUIController
from app.cnc_programmer.rpi_board import RPiBoard
from app.cnc_programmer.dps_mode import DPSMode
from app.cnc_programmer.stepper.position import Axis
from app.cnc_programmer.stepper.stepper_driver import StepperDriver
from app.cnc_programmer.tester import Tester
# from app.cnc_programmer.gui.gui import GUIController


## LEVEL 1 PRIORITIES ##
# TODO: GUI
# TODO: Z Axis
# TODO:

## LEVEL 2 PRIORITIES ##
# TODO: logging
# TODO: RUN as process

class CNCRunner:

    DEFAULT_Z_HEIGHT = 7.5
    DEFAULT_SPEED = 100

    def __init__(self) -> None:
        self.board = RPiBoard()
        self.stepper_driver = StepperDriver(self.board)
        self.programmer = DPSProgrammer()
        self.tester = Tester(self.board)

        self.gui_controller: GUIController = None

        # variables shared with GUI
        self.config: CNCProgrammerConfig = None
        self.selected_firmware_config: FirmwareConfig = None
        self.selected_plate_config: PlateConfig = None

        self.programming_all_plates: bool = False
        self.dps_logs: dict[(int, int), DPSLog] = {}
        self.dps_under_test_running: bool = False
        self.dps_under_test_mode: DPSMode = None

        # threading
        self.thread_should_run: bool = True
        self.worker_thread = threading.Thread(target=self.worker)
        print("CNC Programmer was successfully initialized...")

    def set_controller(self, gui_controller: GUIController) -> None:
        self.gui_controller = gui_controller

    def set_config(self, config: CNCProgrammerConfig) -> None:
        self.config = config
        self.selected_firmware_config = list(config.firmware_configs.values())[0]
        self.selected_plate_config = list(config.plate_configs.values())[0]
        self.programmer.set_config(config.pickle_default_path, config.firmware_default_path)

    def set_running(self, running: bool) -> None:
        self.programming_all_plates = running
        self.stepper_driver.running = running

    def process_dps(self) -> DPSLog:
        # create a new dps log instance
        dps_log = DPSLog()
        # turn on power supply of DPS
        self.board.dps_activate()
        # program firmware
        exited_program: CompletedProcess = self.programmer.load()
        # deinit ISCP pins
        self.board.inactivate_ISCP_pins()

        # set DPS log
        dps_log.fw_uploaded = exited_program.returncode == 0
        #TODO: review
        # dps_log.fw_upload_message = exited_program.stdout if exited_program.returncode == 0 else exited_program.stderr
        dps_log.fw_upload_message = exited_program.stdout

        if exited_program.returncode == 0:
            # wait until stable TODO: is it needed?
            time.sleep(2)
            # measure button LED voltage (in the strong lighting mode)
            button_led_voltage_passed, button_led_voltage = self.tester.test_button_LED_voltage(self.selected_firmware_config)
            # measure current in the strong lighting mode
            self.dps_under_test_mode = DPSMode.STRONG
            led_current_strong_mode_passed, led_current_strong_mode = self.tester.test_LED_current(self.selected_firmware_config, self.dps_under_test_mode)
            # increase the lighting mode
            self.increase_dps_under_test_mode()
            # wait until stable TODO: is it needed?
            time.sleep(2)
            # measure current in the low lighting mode
            led_current_light_mode_passed, led_current_light_mode = self.tester.test_LED_current(self.selected_firmware_config, self.dps_under_test_mode)

            # set DPS log
            dps_log.led_current_mode1_passed = led_current_strong_mode_passed
            dps_log.led_current_mode1 = led_current_strong_mode
            dps_log.led_current_mode2_passed = led_current_light_mode_passed
            dps_log.led_current_mode2 = led_current_light_mode
            dps_log.button_led_voltage_passed = button_led_voltage_passed
            dps_log.button_led_voltage = button_led_voltage

        # turn off DPS power supply
        self.board.dps_inactivate()

        return dps_log

    def increase_dps_under_test_mode(self) -> None:
        self.dps_under_test_mode = DPSMode.increase_mode(self.dps_under_test_mode)
        self.board.dps_button_hold(self.selected_firmware_config.button_led_mode_change_duration / 1000)


    # Assumes that the CNC is placed in position [0,0]
    def start_programming_dps_plate(self) -> None:
        logging.info("DPS plate is about to be programmed...")
        self.dps_logs = {}

        for row in range(self.selected_plate_config.rows):
            for column in range(self.selected_plate_config.columns):
                # break condition
                if not self.programming_all_plates: return
                # if the row is even ---> increase column, if odd <--- decrease column
                column = column if row % 2 == 0 else self.selected_plate_config.columns - column - 1
                pos_target_x_mm: float = column * self.selected_plate_config.x_spacing + self.selected_plate_config.x_offset
                pos_target_y_mm: float = row * self.selected_plate_config.y_spacing + self.selected_plate_config.y_offset

                logging.info(f"Moving to position: [{column}, {row}], [{pos_target_x_mm} mm, {pos_target_y_mm} mm]")
                self.stepper_driver.go(Axis.X, pos_target_x_mm, CNCRunner.DEFAULT_SPEED)
                time.sleep(0.1)
                self.stepper_driver.go(Axis.Y, pos_target_y_mm, CNCRunner.DEFAULT_SPEED)
                time.sleep(0.1)
                # skip the movement in Z axis on start
                if not (row == 0 and column == 0):
                    self.stepper_driver.go(Axis.Z, 0, CNCRunner.DEFAULT_SPEED)
                time.sleep(1)

                logging.info(f"DPS programming starting...")
                self.dps_under_test_running = True
                dps_log: DPSLog = self.process_dps()
                self.dps_under_test_running = False
                logging.info(f"DPS programming finished...")
                dps_log.x = column
                dps_log.y = row
                self.dps_logs[(column, row)] = dps_log

                self.stepper_driver.go(Axis.Z, CNCRunner.DEFAULT_Z_HEIGHT, 100)

                # update gui controller
                self.gui_controller.ex_evt_update_dps_log(dps_log)

        self.stepper_driver.go_home(100)
        self.programming_all_plates = False

        # update gui controller
        self.gui_controller.ex_evt_process_completed()

    def move(self, axis: Axis, step: float) -> None:
        logging.info(f"Moving {step} mm in axis {axis.name}")
        self.stepper_driver.reset_pos()
        self.stepper_driver.go(axis, step, CNCRunner.DEFAULT_SPEED)
        logging.info(f"Moving completed")

    def start(self):
        self.worker_thread.start()

    def stop(self):
        self.thread_should_run = False
        self.worker_thread.join(0.1)

    def is_alive(self):
        return self.worker_thread.is_alive()

    def worker(self):
        while self.thread_should_run:
            if self.programming_all_plates:
                self.start_programming_dps_plate()
            time.sleep(0.1)


def test():
    logging.basicConfig(level=logging.DEBUG)

    config = CNCProgrammerConfigParser(f"./resources/config_cnc_programmer.conf").parse_config()
    print(config)
    programmer = CNCRunner()
    programmer.start()
    programmer.set_config(config)
    programmer.programming_all_plates = True

    try:
        while True:
            time.sleep(1)
            pass
    except KeyboardInterrupt:
        print("Exiting...")
        programmer.stop()
    # programmer.start_programming_dps_plate()

def test_processing():
    config = CNCProgrammerConfigParser(f"./resources/config_cnc_programmer.conf").parse_config()
    programmer = CNCRunner()
    programmer.set_config(config)
    log = programmer.process_dps()
    print(log)


if __name__ == "__main__":
    test()
