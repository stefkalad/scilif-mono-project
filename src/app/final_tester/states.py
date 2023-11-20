from __future__ import annotations

import logging
import time

from app.final_tester.gui.gui import GUIController, Pins
# from app.final_tester.final_tester import FinalTester
from app.final_tester.rpi_board import RPiBoard


class State:
    def __init__(self, tester: "FinalTester") -> None:
        self.tester = tester
        self.board: RPiBoard = tester.board
        self.gui_controller: GUIController = tester.gui_controller

    def run(self) -> "State" | None:
        assert 0, "run not implemented"


class State_0(State):
    # NOTE: waiting for start button press

    def run(self) -> State | None:
        logging.info("[State 0] Entering --> waiting for start button")
        while self.board.start_in_pin.value is False:
            if self.tester.stopped(): return None
            time.sleep(0.1)
        time.sleep(RPiBoard.WAIT_TIME_AFTER_INPUT_READ)
        logging.info("[State 0] Start button pressed --> leaving to State 1")
        self.gui_controller.ex_evt_clear_measurement_output()
        return State_1(self.tester)


class State_1(State):
    # -- start button pressed, button not pressed
    # -- write 1 to axis 1 and wait until it is completed

    def run(self) -> State | None:

        logging.info("[State 1] Entering --> checking binder")
        binder_input: bool = self.board.binder_in_pin.value
        if binder_input is False:
            logging.info("[State 1] The device is not based in the binder --> leaving to State 0")
            return State_0(self.tester)
        else:
            # move axis 1
            logging.info("[State 1] Sliding out in axis 1 --> waiting for process to complete")
            self.board.axis_1_movement_out_pin.value = True
            # wait until axis 1 completed
            while self.board.axis_1_movement_in_pin.value is False:
                if self.tester.stopped(): return None
                time.sleep(0.1)
            time.sleep(RPiBoard.WAIT_TIME_AFTER_INPUT_READ)
            logging.info("[State 1] Sliding out completed  --> leaving to State 2")
            return State_2(self.tester)


class State_2(State):
    # -- axis 1 completed
    # -- write 1 to axis 2 and wait until it is completed, wait 3 seconds, write 0 and wait until it is completed

    def run(self) -> State | None:

        logging.info("[State 2] Entering, pressing button in axis 2 --> waiting for process to complete")

        # move axis 2
        self.board.axis_2_movement_out_pin.value = True
        # wait until axis 2 completed
        while self.board.axis_2_movement_in_pin.value is False:
            if self.tester.stopped(): return None
            time.sleep(0.1)
        time.sleep(RPiBoard.WAIT_TIME_AFTER_INPUT_READ)
        logging.info("[State 2] Pressing button in axis 2 completed --> waiting for 3 seconds")

        # wait 3 seconds to press the button
        time.sleep(3)
        logging.info("[State 2] Waiting completed, releasing button in axis 2 --> waiting for process to complete")

        # move axis 2
        self.board.axis_2_movement_out_pin.value = False
        # wait until axis 2 completed
        while self.board.axis_2_movement_in_pin.value is True:
            if self.tester.stopped(): return None
            time.sleep(0.1)
        time.sleep(RPiBoard.WAIT_TIME_AFTER_INPUT_READ)
        logging.info("[State 2] Releasing button in axis 2 completed --> leaving to State 3")
        return State_3(self.tester)


class State_3(State):
    # -- axis 1 completed, button pressed
    # -- write 1 to axis 1 and wait until it is completed

    def run(self) -> State | None:
        logging.info("[State 3] Entering, sliding back in axis 1 --> waiting for process to complete")
        # move axis 1
        self.board.axis_1_movement_out_pin.value = False
        # wait until axis 1 completed
        while self.board.axis_1_movement_in_pin.value is True:
            if self.tester.stopped(): return None
            time.sleep(0.1)
        time.sleep(RPiBoard.WAIT_TIME_AFTER_INPUT_READ)

        logging.info("[State 3] Sliding back completed")
        logging.info("[State 3] Processing started")
        # process DSP
        self.process()
        self.gui_controller.ex_evt_show_measurement_output()
        self.gui_controller.ex_evt_show_dialog()
        logging.info("[State 3] Processing completed")

        logging.info("[State 3] Releasing the device --> leaving to State 0")
        self.board.binder_out_pin.value = True
        return State_0(self.tester)

    def process(self):
        time.sleep(1)




