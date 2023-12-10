from __future__ import annotations

import logging
import threading
import time
from subprocess import CompletedProcess
from typing import List, Tuple

from app.cnc_programmer.config.config import CNCProgrammerConfig
from app.cnc_programmer.config.config_parser import CNCProgrammerConfigParser
from app.cnc_programmer.config.firmware import FirmwareConfig
from app.cnc_programmer.config.plate import PlateConfig
from app.cnc_programmer.dps_log import DPSLog
from app.cnc_programmer.dps_mode import FirmwareType
from app.cnc_programmer.dps_programmer import DPSProgrammer
from app.cnc_programmer.gui.gui_controller import GUIController
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

    DEFAULT_Z_HEIGHT = 12
    DEFAULT_Z_SAFE_HEIGHT = 8  #z position when an initial lift is undertaken or verification from operator is needed
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
        self.current_cycle_pos: Tuple[int, int] = None
        #either [x,y] in mm if state is MOVING or [x,y] DPS if state is AUTOMATIC_CYCLE
        self.state_moving_params: dict[str, float | int | Axis] = {
            'start_from_x': 0, 'start_from_y': 0,
            'step_mm': 0, 'axis:': 0,
        }

        self.dps_logs: dict[(int, int), DPSLog] = {}

        self.dps_under_test_running: bool = False

        # threading
        self.threads_should_run: bool = True
        self.worker_thread = threading.Thread(target=self.worker)
        self.pos_thread = threading.Thread(target=self.pos_worker)
        logging.info("[CNC]: Programmer was successfully initialized...")

    def set_controller(self, gui_controller: GUIController) -> None:
        self.gui_controller = gui_controller

    def set_config(self, config: CNCProgrammerConfig) -> None:
        self.config = config
        self.selected_firmware_config = list(config.firmware_configs.values())[0]
        self.selected_plate_config = list(config.plate_configs.values())[0]
        self.programmer.set_config(config.pickle_default_path, self.selected_firmware_config.path)

    # region STATE MACHINE
    def set_home(self) -> None:
        logging.info("[CNC]: Setting new HOME position")
        assert self.state == CNCRunnerState.STOPPED

        self.stepper_driver.reset_pos()
        self.gui_controller.ex_evt_update_current_pos(0, 0)
        self.gui_controller.ex_evt_update_current_pos_mm([0, 0, 0])

    def set_stop(self) -> None:
        logging.info("[CNC]: Movement stopped")
        assert self.state == CNCRunnerState.MOVING_HOME or self.state == CNCRunnerState.MOVING_BY_STEP

        self.state = CNCRunnerState.STOPPED
        self.stepper_driver.running = False

    def set_moving(self, axis: Axis, step_mm: float) -> None:
        logging.info(f"[CNC]: Moving by step {step_mm} in axis {axis.name}")
        assert self.state == CNCRunnerState.STOPPED

        self.state = CNCRunnerState.MOVING_BY_STEP
        self.state_moving_params['axis'] = axis
        self.state_moving_params['step'] = step_mm
        self.stepper_driver.running = True

    def set_moving_home(self) -> None:
        logging.info(f"[CNC]: Moving to home position")
        assert self.state == CNCRunnerState.STOPPED

        self.state = CNCRunnerState.MOVING_HOME
        self.stepper_driver.running = True

    def set_in_automatic_cycle(self, start_from_x: int, start_from_y: int) -> None:
        logging.info(f"[CNC]: New automatic cycle started")
        assert self.state == CNCRunnerState.STOPPED or self.state == CNCRunnerState.PAUSED_IN_AUTOMATIC_CYCLE

        self.state = CNCRunnerState.IN_AUTOMATIC_CYCLE
        self.dps_logs = {}
        self.current_cycle_pos = None
        self.state_moving_params['start_from_x'] = start_from_x
        self.state_moving_params['start_from_y'] = start_from_y
        self.stepper_driver.running = True

    def set_paused_in_automatic_cycle(self) -> None:
        logging.info(f"[CNC]: Automatic cycle stopped")
        assert self.state == CNCRunnerState.IN_AUTOMATIC_CYCLE

        self.state = CNCRunnerState.PAUSED_IN_AUTOMATIC_CYCLE
        self.stepper_driver.running = False

    def set_resume_automatic_cycle(self) -> None:
        logging.info(f"[CNC]: Automatic cycle resumed")
        assert self.state == CNCRunnerState.PAUSED_IN_AUTOMATIC_CYCLE

        self.set_in_automatic_cycle(*self.next_position_in_sequence())

    def set_completed_automatic_cycle(self) -> None:
        logging.info(f"[CNC]: Automatic cycle completed")
        assert self.state == CNCRunnerState.IN_AUTOMATIC_CYCLE or self.state == CNCRunnerState.PAUSED_IN_AUTOMATIC_CYCLE #case of stop event in last motion

        self.state = CNCRunnerState.COMPLETED_AUTOMATIC_CYCLE

    def set_finish_automatic_cycle(self) -> None:
        logging.info(f"[CNC]: Automatic cycle stopped")
        assert self.state == CNCRunnerState.PAUSED_IN_AUTOMATIC_CYCLE or self.state == CNCRunnerState.COMPLETED_AUTOMATIC_CYCLE

        self.state = CNCRunnerState.STOPPED
        self.dps_logs = {}
        self.current_cycle_pos = None

    # endregion STATE MACHINE

    # region DPS PROCESSORS
    def process_dps(self) -> DPSLog:
        # prepare DPS
        self.tester.prepare_dps()
        # create a new dps log instance
        dps_log = DPSLog()
        # program firmware
        exited_program: CompletedProcess = self.programmer.load()

        #TODO: TURNOV check
        #dps_log.fw_uploaded = exited_program.returncode == 0 and len(exited_program.stdout) == 0
        dps_log.fw_uploaded = exited_program.returncode == 0
        dps_log.fw_upload_message = exited_program.stdout

        if exited_program.returncode == 0:
            if self.selected_firmware_config.type == FirmwareType.FLASH:
                self.tester.test_dps_flash(self.selected_firmware_config, dps_log)
            elif self.selected_firmware_config.type == FirmwareType.MAX_ONLY:
                self.tester.test_dps_maxonly(self.selected_firmware_config, dps_log)
        return dps_log
    # endregion DPS PROCESSORS

    def generate_position_sequence(self, start_from_x: int, start_from_y: int) -> List[(int, int)]:
        pos_list = []
        for row in range(self.selected_plate_config.rows):
            for column in range(self.selected_plate_config.columns):
                # if the row is even ---> increase column, if odd <--- decrease column
                column = column if row % 2 == 0 else self.selected_plate_config.columns - column - 1
                pos_list.append((column, row))

        return pos_list[pos_list.index((start_from_x, start_from_y)):]

    def next_position_in_sequence(self) -> Tuple[int, int]:
        if self.current_cycle_pos is None: return 0, 0
        next_positions: List[(int, int)] = self.generate_position_sequence(*self.current_cycle_pos)[1:]
        return next_positions[0] if len(next_positions) else None

    def is_safe_z_lift_needed(self, pos_target_x_mm: float, pos_target_y_mm: float) -> bool:
        pos_current_mm: [float, float, float] = self.stepper_driver.get_current_pos_mm()

        return pos_current_mm[Axis.Z.value] < self.config.z_minimum_safe_height_mm and (
                abs(pos_current_mm[Axis.X.value] - pos_target_x_mm) > 0.1 or
                abs(pos_current_mm[Axis.Y.value] - pos_target_y_mm) > 0.1)

    def cycle(self, start_from_x: int = 0, start_from_y: int = 0) -> None:
        logging.info("[CNC]: DPS plate is about to be programmed...")
        logging.info(f"[CNC]: DPS starting from pos: [{start_from_x},{start_from_y}]")

        # initial move in Z axis to the safe height
        if self.is_safe_z_lift_needed(start_from_x * self.selected_plate_config.x_spacing, start_from_y * self.selected_plate_config.y_spacing):
            logging.info("[CNC] Moving to safe position in Z axis")
            self.stepper_driver.go_to_pos_mm(Axis.Z, self.config.z_moving_height_mm, CNCRunner.DEFAULT_SPEED)

        generated_positions: List[int, int] = self.generate_position_sequence(start_from_x, start_from_y)

        for column, row in generated_positions:

            # calculate the absolute positions
            pos_target_x_mm: float = column * self.selected_plate_config.x_spacing + self.selected_plate_config.x_offset
            pos_target_y_mm: float = row * self.selected_plate_config.y_spacing + self.selected_plate_config.y_offset
            logging.info(f"[CNC]: Moving to position: [{column}, {row}], [{pos_target_x_mm} mm, {pos_target_y_mm} mm]")

            # update gui controller
            self.gui_controller.ex_evt_update_current_pos(column, row)
            # go
            self.stepper_driver.go_to_pos_mm(Axis.X, pos_target_x_mm, CNCRunner.DEFAULT_SPEED, 0.0)
            self.stepper_driver.go_to_pos_mm(Axis.Y, pos_target_y_mm, CNCRunner.DEFAULT_SPEED, 0.25)
            self.stepper_driver.go_to_pos_mm(Axis.Z, 0, CNCRunner.DEFAULT_SPEED, 0.25)

            # break condition
            if self.state is not CNCRunnerState.IN_AUTOMATIC_CYCLE:
                # exit application condition
                assert self.state == CNCRunnerState.PAUSED_IN_AUTOMATIC_CYCLE or self.state == CNCRunnerState.STOPPED
                logging.info("[CNC] Leaving automatic cycle")
                return

            # update current position
            self.current_cycle_pos = (column, row)

            logging.info(f"[CNC]: DPS [{column},{row}] programming starting")
            self.dps_under_test_running = True
            dps_log: DPSLog = self.process_dps()
            self.dps_under_test_running = False
            logging.info(f"[CNC]: DPS [{column},{row}] programming finished")
            dps_log.x, dps_log.y = column, row
            self.dps_logs[(column, row)] = dps_log

            self.stepper_driver.go_to_pos_mm(Axis.Z, self.config.z_moving_height_mm, CNCRunner.DEFAULT_SPEED, 0.0)

            # update gui controller
            self.gui_controller.ex_evt_update_dps_log(dps_log)

        # move away from last position
        self.stepper_driver.move(Axis.Y, 50, 100)
        # complete
        self.set_completed_automatic_cycle()
        # update gui controller
        self.gui_controller.ex_evt_automatic_cycle_completed()
        logging.info(f"[CNC]: DPC programming cycle completed -> stopping")

    def move(self, axis: Axis, step_mm: float) -> None:
        logging.info(f"[CNC]: Moving {step_mm} mm along axis {axis.name}")
        self.stepper_driver.move(axis, step_mm, CNCRunner.DEFAULT_SPEED)
        if self.state == CNCRunnerState.MOVING_BY_STEP:
            self.set_stop()
            self.gui_controller.ex_evt_process_completed()
            logging.info(f"[CNC]: Moving completed -> stopping")

    def go_home(self) -> None:
        logging.info("[CNC]: Moving HOME")

        # initial move in Z axis to the safe height
        if self.is_safe_z_lift_needed(0.0, 0.0):
            logging.info("[CNC] Moving to safe position in Z axis")
            self.stepper_driver.go_to_pos_mm(Axis.Z, self.config.z_moving_height_mm, CNCRunner.DEFAULT_SPEED)
        # move home
        self.stepper_driver.go_home(CNCRunner.DEFAULT_SPEED)
        # when the state was not changed
        if self.state == CNCRunnerState.MOVING_HOME:
            self.set_stop()
            self.gui_controller.ex_evt_process_completed()
            logging.info("[CNC]: Moving completed -> stopping")

    def start(self):
        self.worker_thread.start()
        self.pos_thread.start()

    def stop(self):
        logging.info("[CNC]: Stopping application")
        self.threads_should_run = False
        self.state = CNCRunnerState.STOPPED
        self.stepper_driver.running = False

        self.worker_thread.join(2)
        self.pos_thread.join(2)
        self.board.deinit()

    def is_alive(self):
        return self.worker_thread.is_alive() and self.pos_thread.is_alive()

    def worker(self):
        while self.threads_should_run:
            if self.state == CNCRunnerState.IN_AUTOMATIC_CYCLE:
                self.cycle(self.state_moving_params['start_from_x'], self.state_moving_params['start_from_y'])
            elif self.state == CNCRunnerState.MOVING_BY_STEP:
                self.move(Axis(self.state_moving_params['axis']), self.state_moving_params['step'])
            elif self.state == CNCRunnerState.MOVING_HOME:
                self.go_home()
            time.sleep(0.1)

        logging.info("[CNC]: Worker thread exited...")

    def pos_worker(self):
        # wait until everything is set up
        time.sleep(3)
        while self.threads_should_run:
            if self.gui_controller:
                self.gui_controller.ex_evt_update_state(self.state)
                self.gui_controller.ex_evt_update_current_pos_mm(self.stepper_driver.get_current_pos_mm())
            time.sleep(1)
        logging.info("[CNC]: Position thread exited...")


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
    log = programmer.process_dps()
    print(log)


def test_pos_generator():
    config = CNCProgrammerConfigParser(f"./resources/config_cnc_programmer.conf").parse_config()
    programmer = CNCRunner()
    programmer.set_config(config)
    pos_list = programmer.generate_position_sequence(0, 0)
    print(pos_list)


if __name__ == "__main__":
    test_pos_generator()

