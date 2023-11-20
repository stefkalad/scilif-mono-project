import logging
import threading
import time

from app.final_tester.gui.gui import GUIController, Pins
from app.final_tester.rpi_board import RPiBoard
from app.final_tester.states import State, State_0


class FinalTester:

    def __init__(self) -> None:
        self.board = RPiBoard()
        self.gui_controller: GUIController = None

        self.current_state: State

        # threading
        self.threads_should_run: bool = True
        self.state_machine_worker_thread = threading.Thread(target=self.state_machine_worker)
        self.io_worker_thread = threading.Thread(target=self.io_worker)
        logging.info("Final Tester was successfully initialized...")

    def set_controller(self, gui_controller: GUIController) -> None:
        self.gui_controller = gui_controller
        self.current_state = State_0(self)

    def start(self):
        self.state_machine_worker_thread.start()
        self.io_worker_thread.start()

    def stop(self):
        self.threads_should_run = False
        self.state_machine_worker_thread.join(0.1)
        self.io_worker_thread.join(0.1)

    def stopped(self) -> bool:
        return self.threads_should_run is False

    def state_machine_worker(self):
        self.run_state_machine()

    def io_worker(self):
        self.run_io()

    def run_state_machine(self) -> None:
        next_state = self.current_state.run()
        while next_state is not None and self.threads_should_run:
            self.current_state = next_state
            next_state = self.current_state.run()

    def run_io(self) -> None:

        while self.threads_should_run is True:
            self.gui_controller.ex_evt_change_input_pin(Pins.START, self.board.start_in_pin.value)
            self.gui_controller.ex_evt_change_input_pin(Pins.BINDER, self.board.binder_in_pin.value)
            self.gui_controller.ex_evt_change_input_pin(Pins.AXIS_1, self.board.axis_1_movement_in_pin.value)
            self.gui_controller.ex_evt_change_input_pin(Pins.AXIS_2, self.board.axis_2_movement_in_pin.value)

            self.gui_controller.ex_evt_change_output_pin(Pins.BINDER, self.board.binder_out_pin.value)
            self.gui_controller.ex_evt_change_output_pin(Pins.AXIS_1, self.board.axis_1_movement_out_pin.value)
            self.gui_controller.ex_evt_change_output_pin(Pins.AXIS_2, self.board.axis_2_movement_out_pin.value)

            time.sleep(1)




