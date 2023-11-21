from __future__ import annotations

import logging
import threading
import time
from subprocess import CompletedProcess
from typing import List

from app.cnc_programmer.config.config import CNCProgrammerConfig
from app.cnc_programmer.config.config_parser import CNCProgrammerConfigParser
from app.cnc_programmer.config.firmware import FirmwareConfig
from app.cnc_programmer.config.plate import PlateConfig
from app.cnc_programmer.dps_log import DPSLog
from app.cnc_programmer.dps_mode import DPSMode, DPSFlashMode, DPSMaxOnlyMode, FirmwareType
from app.cnc_programmer.dps_programmer import DPSProgrammer
from app.cnc_programmer.gui.gui import GUIController
from app.cnc_programmer.rpi_board import RPiBoard
from app.cnc_programmer.stepper.position import Axis
from app.cnc_programmer.stepper.state import CNCRunnerState
from app.cnc_programmer.stepper.stepper_driver import StepperDriver
from app.cnc_programmer.tester import Tester


# from app.cnc_programmer.gui.gui import GUIController

## LEVEL 2 PRIORITIES ##
# TODO: logging
# TODO: RUN as process

class CNCRunner:

    DEFAULT_Z_HEIGHT = 7.5

    DEFAULT_Z_INITIAL_LIFT_THRESHOLD = 5 # z position when an initial lift is undertaken
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

        self.state: CNCRunnerState = CNCRunnerState.STOPPED
        #either [x,y] in mm if state is MOVING or [x,y] DPS if state is AUTOMATIC_CYCLE
        self.state_moving_params: dict[str, float | int] = {
            'start_from_x': 0, 'start_from_y': 0,
            'step_mm': 0, 'axis:': 0,
        }

        self.dps_logs: dict[(int, int), DPSLog] = {}
        self.dps_under_test_running: bool = False
        self.dps_under_test_mode: DPSMode = None

        # threading
        self.thread_should_run: bool = True
        self.worker_thread = threading.Thread(target=self.worker)
        logging.info("[CNC]: Programmer was successfully initialized...")

    def set_controller(self, gui_controller: GUIController) -> None:
        self.gui_controller = gui_controller

    def set_config(self, config: CNCProgrammerConfig) -> None:
        self.config = config
        self.programmer.set_config(config.pickle_default_path, config.firmware_default_path)

    def set_selected_firmware_config(self, firmware_config: FirmwareConfig) -> None:
        self.selected_firmware_config = firmware_config

    def set_selected_plate_config(self, plate_config: PlateConfig) -> None:
        self.selected_plate_config = plate_config

    def set_cycle(self, start_from_x: int, start_from_y: int) -> None:
        self.state = CNCRunnerState.AUTOMATIC_CYCLE
        self.dps_logs = {}
        self.state_moving_params['start_from_x'] = start_from_x
        self.state_moving_params['start_from_y'] = start_from_y
        self.stepper_driver.running = True

    def set_moving(self, axis: int, step_mm: float) -> None:
        self.state = CNCRunnerState.MOVING_BY_STEP
        self.state_moving_params['axis'] = axis
        self.state_moving_params['step'] = step_mm
        self.stepper_driver.running = True

    def set_stop(self) -> None:
        logging.info("[CNC] Runner stopped")
        self.state = CNCRunnerState.STOPPED
        self.stepper_driver.running = False

    def set_home(self) -> None:
        logging.info("[CNC]: Setting new HOME position")
        self.stepper_driver.reset_pos()
        self.gui_controller.ex_evt_update_current_pos(0, 0)
        self.gui_controller.ex_evt_update_current_pos_mm([0, 0, 0])

    def set_go_home(self) -> None:
        self.state = CNCRunnerState.MOVING_HOME
        self.stepper_driver.running = True

    def process_dps_flash(self) -> DPSLog:
        # prepare DPS
        self.prepare_dps()
        # create a new dps log instance
        dps_log = DPSLog()
        # program firmware
        exited_program: CompletedProcess = self.programmer.load()

        if exited_program.returncode == 0:
            # wait until stable
            time.sleep(1.5)
            # measure button LED voltage (in the strong lighting mode)
            button_led_voltage_passed, button_led_voltage = self.tester.test_button_LED_voltage(self.selected_firmware_config)
            # measure current in the strong lighting mode
            self.dps_under_test_mode = DPSFlashMode.STRONG
            led_current_strong_mode_passed, led_current_strong_mode = self.tester.test_LED_current(self.selected_firmware_config, FirmwareType.FLASH, self.dps_under_test_mode)
            # increase the lighting mode
            self.increase_dps_under_test_mode()
            # wait until stable
            time.sleep(0.5)
            # measure current in the low lighting mode
            led_current_light_mode_passed, led_current_light_mode = self.tester.test_LED_current(self.selected_firmware_config, FirmwareType.FLASH, self.dps_under_test_mode)

            # set DPS log
            dps_log.led_current_mode1_passed = led_current_strong_mode_passed
            dps_log.led_current_mode1 = led_current_strong_mode
            dps_log.led_current_mode2_passed = led_current_light_mode_passed
            dps_log.led_current_mode2 = led_current_light_mode
            dps_log.button_led_voltage_passed = button_led_voltage_passed
            dps_log.button_led_voltage = button_led_voltage

        dps_log.fw_uploaded = exited_program.returncode == 0
        #TODO: review
        # dps_log.fw_upload_message = exited_program.stdout if exited_program.returncode == 0 else exited_program.stderr
        dps_log.fw_upload_message = exited_program.stdout

        # turn off DPS power supply
        self.board.dps_inactivate()

        return dps_log

    def process_dps_maxonly(self) -> DPSLog:
        # prepare DPS
        self.prepare_dps()
        # create a new dps log instance
        dps_log = DPSLog()
        # program firmware
        exited_program: CompletedProcess = self.programmer.load()

        if exited_program.returncode == 0 and len(exited_program.stdout) == 0:
            # wait until stable
            time.sleep(0.5)
            # increase the lighting mode
            self.dps_under_test_mode = DPSMaxOnlyMode.NO
            self.increase_dps_under_test_mode()
            # wait until stable
            time.sleep(0.5)
            # measure button LED voltage (in the strong lighting mode)
            button_led_voltage_passed, button_led_voltage = self.tester.test_button_LED_voltage(self.selected_firmware_config)
            # measure current in the low lighting mode
            led_current_strong_mode_passed, led_current_strong_mode = self.tester.test_LED_current(self.selected_firmware_config, FirmwareType.MAX_ONLY, self.dps_under_test_mode)

            # set DPS log
            dps_log.led_current_mode1_passed = led_current_strong_mode_passed
            dps_log.led_current_mode1 = led_current_strong_mode
            dps_log.button_led_voltage_passed = button_led_voltage_passed
            dps_log.button_led_voltage = button_led_voltage

        # set DPS log
        dps_log.fw_uploaded = exited_program.returncode == 0 and len(exited_program.stdout) == 0
        dps_log.fw_upload_message = exited_program.stdout
        # turn off DPS power supply
        self.board.dps_inactivate()
        return dps_log

    def increase_dps_under_test_mode(self) -> None:
        self.dps_under_test_mode = self.dps_under_test_mode.__class__.increase_mode(self.dps_under_test_mode)
        self.board.dps_button_hold(self.selected_firmware_config.button_led_mode_change_duration / 1000)

    def prepare_dps(self) -> None:
        # set offset of ADC for ACS723 (inactivate ISCP pins to do so)
        self.board.inactivate_ISCP_pins()
        self.tester.set_LED_current_offset()
        # turn on power supply of DPS
        self.board.dps_activate()

    def generate_position_sequence(self, start_from_x: int, start_from_y: int) -> List[(int, int)]:
        pos_list = []
        for row in range(self.selected_plate_config.rows):
            for column in range(self.selected_plate_config.columns):
                # if the row is even ---> increase column, if odd <--- decrease column
                column = column if row % 2 == 0 else self.selected_plate_config.columns - column - 1
                pos_list.append((column, row))

        return pos_list[pos_list.index((start_from_x, start_from_y)):]

    def cycle(self, start_from_x: int = 0, start_from_y: int = 0) -> None:
        logging.info("[CNC]: DPS plate is about to be programmed...")
        logging.info(f"[CNC]: DPS starting from pos: [{start_from_x},{start_from_y}]")

        pos_current_mm = self.stepper_driver.get_current_pos_mm()
        # initial move in Z axis to the safe height
        if pos_current_mm[Axis.Z.value] < CNCRunner.DEFAULT_Z_INITIAL_LIFT_THRESHOLD and (
            abs(pos_current_mm[Axis.X.value] - start_from_x * self.selected_plate_config.x_spacing) > 0.1 or
            abs(pos_current_mm[Axis.Y.value] - start_from_y * self.selected_plate_config.y_spacing) > 0.1):
            logging.info("[CNC] Moving to safe position in Z axis")
            self.stepper_driver.go_to_pos_mm(Axis.Z, CNCRunner.DEFAULT_Z_HEIGHT, CNCRunner.DEFAULT_SPEED)

        for (column, row) in self.generate_position_sequence(start_from_x, start_from_y):

            pos_target_x_mm: float = column * self.selected_plate_config.x_spacing + self.selected_plate_config.x_offset
            pos_target_y_mm: float = row * self.selected_plate_config.y_spacing + self.selected_plate_config.y_offset

            logging.info(f"[CNC]: Moving to position: [{column}, {row}], [{pos_target_x_mm} mm, {pos_target_y_mm} mm]")
            # update GUI
            self.gui_controller.ex_evt_update_current_pos(column, row)
            # go
            self.stepper_driver.go_to_pos_mm(Axis.X, pos_target_x_mm, CNCRunner.DEFAULT_SPEED)
            time.sleep(0.1)
            self.stepper_driver.go_to_pos_mm(Axis.Y, pos_target_y_mm, CNCRunner.DEFAULT_SPEED)
            time.sleep(0.1)
            self.stepper_driver.go_to_pos_mm(Axis.Z, 0, CNCRunner.DEFAULT_SPEED)
            time.sleep(1)

            # break condition
            if self.state is not CNCRunnerState.AUTOMATIC_CYCLE:
                logging.info("[CNC] Leaving automatic cycle")
                return

            logging.info(f"[CNC]: DPS [{column},{row}] programming starting")
            self.dps_under_test_running = True
            dps_log: DPSLog = self.process_dps_maxonly()
            self.dps_under_test_running = False
            logging.info(f"[CNC]: DPS [{column},{row}] programming finished")
            dps_log.x = column
            dps_log.y = row
            self.dps_logs[(column, row)] = dps_log

            self.stepper_driver.go_to_pos_mm(Axis.Z, CNCRunner.DEFAULT_Z_HEIGHT, CNCRunner.DEFAULT_SPEED)

            # update gui controller
            self.gui_controller.ex_evt_update_dps_log(dps_log)
            self.gui_controller.ex_evt_update_current_pos_mm(self.stepper_driver.get_current_pos_mm())

        # move away from last position
        self.stepper_driver.move(Axis.Y, 50, 100)
        # stop
        self.set_stop()
        # update gui controller
        self.gui_controller.ex_evt_update_current_pos_mm(self.stepper_driver.get_current_pos_mm())
        self.gui_controller.ex_evt_automatic_cycle_completed()
        logging.info(f"[CNC]: DPC programming cycle completed -> stopping")

    def move(self, axis: Axis, step_mm: float) -> None:
        logging.info(f"[CNC]: Moving {step_mm} mm along axis {axis.name}")
        self.stepper_driver.move(axis, step_mm, CNCRunner.DEFAULT_SPEED)
        self.set_stop()
        self.gui_controller.ex_evt_update_current_pos_mm(self.stepper_driver.get_current_pos_mm())
        self.gui_controller.ex_evt_process_completed()
        logging.info(f"[CNC]: Moving completed -> stopping")

    def go_home(self) -> None:
        logging.info(f"[CNC]: Moving HOME")
        self.stepper_driver.go_home(CNCRunner.DEFAULT_SPEED)
        self.set_stop()
        self.gui_controller.ex_evt_update_current_pos_mm(self.stepper_driver.get_current_pos_mm())
        self.gui_controller.ex_evt_process_completed()
        logging.info(f"[CNC]: Moving completed -> stopping")

    def start(self):
        self.worker_thread.start()

    def stop(self):
        self.thread_should_run = False
        self.worker_thread.join(0.1)
        self.board.deinit()

    def is_alive(self):
        return self.worker_thread.is_alive()

    def worker(self):
        while self.thread_should_run:
            if self.state == CNCRunnerState.AUTOMATIC_CYCLE:
                self.cycle(self.state_moving_params['start_from_x'], self.state_moving_params['start_from_y'])
            elif self.state == CNCRunnerState.MOVING_BY_STEP:
                self.move(Axis(self.state_moving_params['axis']), self.state_moving_params['step'])
            elif self.state == CNCRunnerState.MOVING_HOME:
                self.go_home()

            time.sleep(0.1)


def test():
    logging.basicConfig(level=logging.DEBUG)

    config = CNCProgrammerConfigParser(f"./resources/config_cnc_programmer.conf").parse_config()
    print(config)
    programmer = CNCRunner()
    programmer.start()
    programmer.set_config(config)
    programmer.in_automatic_cycle = True

    try:
        while True:
            time.sleep(1)
            pass
    except KeyboardInterrupt:
        print("Exiting...")
        programmer.stop()
    # programmer.start_programming_dps_plate()

def test_processing():
    logging.getLogger().setLevel(logging.INFO)

    config = CNCProgrammerConfigParser(f"./resources/config_cnc_programmer.conf").parse_config()
    programmer = CNCRunner()
    programmer.set_config(config)
    log = programmer.process_dps_maxonly()
    print(log)

def test_pos_generator():
    config = CNCProgrammerConfigParser(f"./resources/config_cnc_programmer.conf").parse_config()
    programmer = CNCRunner()
    programmer.set_config(config)
    programmer.set_selected_plate_config(list(config.plate_configs.values())[0])
    pos_list = programmer.generate_position_sequence(0, 0)
    print(pos_list)

if __name__ == "__main__":
    test_pos_generator()

