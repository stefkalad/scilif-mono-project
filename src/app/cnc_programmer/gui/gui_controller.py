from __future__ import annotations

import logging
import os
import tkinter as tk
from tkinter import filedialog, messagebox, END
from typing import Callable
from typing import TYPE_CHECKING

from app.cnc_programmer.config.config import CNCProgrammerConfig
from app.cnc_programmer.config.config_parser import CNCProgrammerConfigParser
from app.cnc_programmer.config.firmware import FirmwareConfig
from app.cnc_programmer.config.plate import PlateConfig
from app.cnc_programmer.dps_log import DPSLog
from app.cnc_programmer.dps_mode import FirmwareType
from app.cnc_programmer.gui.gui_view import GUIView, Messages, create_root_window, PADX, PADY
from app.cnc_programmer.gui.messages_formatter import MessagesFormatter
from app.cnc_programmer.stepper.position import Axis
from app.cnc_programmer.stepper.state import CNCRunnerState

if TYPE_CHECKING:
    from app.cnc_programmer.cnc_runner import CNCRunner

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

class GUIModel:
    def __init__(self, external: "CNCRunner") -> None:
        self.external: "CNCRunner" = external

        self.home_set: bool = False
        self.uploaded_config_path: str = ''
        self.selected_config_path: str = ''
        self.selected_move_axis: Axis = Axis.X

        # self.selected_plate_config_name: str = ''
        # self.selected_firmware_config_name: str = ''


    @property
    def external_config(self) -> CNCProgrammerConfig | None:
        if self.external is not None:
            return self.external.config
        else:
            logging.error("External CNC runner is not defined!")
            return None

    @external_config.setter
    def external_config(self, config: CNCProgrammerConfig):
        if self.external is not None:
            self.external.set_config(config)
        else:
            logging.error("External CNC runner is not defined!")

    @property
    def selected_plate_config(self) -> PlateConfig | None:
        if self.external is not None:
            return self.external.selected_plate_config
        else:
            logging.error("External CNC runner is not defined!")
            return None

    @property
    def selected_firmware_config(self) -> FirmwareConfig | None:
        if self.external is not None:
            return self.external.selected_firmware_config
        else:
            logging.error("External CNC runner is not defined!")
            return None

    @property
    def external_state(self) -> CNCRunnerState | None:
        if self.external is not None:
            return self.external.state
        else:
            logging.error("External CNC runner is not defined!")
            return None

    @property
    def external_pos(self) -> [float, float, float]:
        if self.external is not None:
            return self.external.stepper_driver.get_current_pos_mm()
        else:
            logging.error("External CNC runner is not defined!")
            return None

    def set_external_state(self, state_setter: Callable[..., None], *args) -> None:
        if self.external is not None:
            state_setter(*args)
        else:
            logging.error("External CNC runner is not defined!")

    def dps_log(self, x: int, y: int) -> DPSLog | None:
        if self.external is not None and self.external.dps_logs.get((x, y)) is not None:
            return self.external.dps_logs[x, y]
        else:
            logging.error("External CNC runner is not defined!")
            return None

class GUIController:

    def __init__(self, view: GUIView, external: "CNCRunner"):
        self.model: GUIModel = GUIModel(external)
        self.view: GUIView = view
        # bind callbacks
        self.bind_callbacks()
        # initial setup
        self.init()

    def bind_callbacks(self) -> None:
        self.view.bind_close_window_cb(self.evt_destroy)
        # settings frame
        self.view.bind_button_click_cb(self.view.browse_files_button, self.evt_browse_files_clicked)
        self.view.bind_button_click_cb(self.view.upload_button, self.evt_upload_config_clicked)
        # automatic cycle frame 
        self.view.bind_button_click_cb(self.view.start_button, self.evt_start_clicked)
        self.view.bind_button_click_cb(self.view.pause_button, self.evt_pause_clicked)
        self.view.bind_button_click_cb(self.view.resume_button, self.evt_resume_clicked)
        self.view.bind_button_click_cb(self.view.finish_button, self.evt_finish_clicked)

        # manual move frame
        self.view.bind_button_click_cb(self.view.manual_stop_button, self.evt_stop_clicked)
        self.view.bind_button_click_cb(self.view.go_home_button, self.evt_go_home_clicked)
        self.view.bind_button_click_cb(self.view.set_home_button, self.evt_set_home_clicked)
        for axis in Axis:
            self.view.bind_button_click_cb(self.view.move_axis_buttons[axis.value], lambda _axis=axis: self.evt_move_axis_clicked(_axis))
        for step in GUIView.STEPS:
            self.view.bind_button_click_cb(self.view.move_distance_buttons[step], lambda _step=step: self.evt_move_distance_clicked(_step))
            self.view.bind_button_click_cb(self.view.move_distance_buttons[-step], lambda _step=-step: self.evt_move_distance_clicked(_step))

    def init(self) -> None:
        # default text
        self.view.set_entry_text(self.view.start_from_x_entry, str(0))
        self.view.set_entry_text(self.view.start_from_y_entry, str(0))
        # buttons default style
        self.view.upload_button.config(style="Accent.TButton")
        self.view.browse_files_button.config(style="Accent.TButton")
        self.view.set_home_button.config(style="Accent.TButton")

        # load default config
        default_config_path: str = f"{ROOT_DIR}/../resources/config_cnc_programmer.conf"
        self.view.set_entry_text(self.view.config_entry, default_config_path)
        self.model.selected_config_path = default_config_path
        self.evt_upload_config_clicked()


    def evt_destroy(self):
        logging.info("[EVT]: Stopping application")
        # destroy runner first (it updates GUI)
        if self.model.external is not None:
            self.model.external.stop()

        self.view.root.destroy()

    def evt_browse_files_clicked(self) -> None:
        #TODO: GUI bg color
        # fd = filedialog.FileDialog(root)
        # file_path = fd.go(pattern="*.conf")
        file_path = filedialog.askopenfilename(initialdir=f"{ROOT_DIR}/../resources", initialfile="config_cnc_programmer.conf", filetypes=[("Config Files", "*.conf")])
        if not file_path or not len(file_path):
            # update view
            self.view.upload_message.config(text=Messages.ERROR_CONFIGURATION_SELECTION.value, foreground="red")
            return
        # update model
        self.model.selected_config_path = file_path
        # update view
        self.view.set_entry_text(self.view.config_entry, file_path)
        self.set_view_state()
        logging.info(f"[GUI]: New configuration file path has been selected {file_path}")

    def evt_upload_config_clicked(self) -> None:
        try:
            config = CNCProgrammerConfigParser(self.model.selected_config_path).parse_config()
            # update model (external)
            selected_firmware_config = list(config.firmware_configs.values())[0]
            selected_plate_config = list(config.plate_configs.values())[0]
            self.model.external_config = config
            self.model.uploaded_config_path = self.model.selected_config_path

            # update view
            # update settings frame
            format_range = lambda range: f"{range[0]} - {range[1]}"
            self.view.upload_message.config(text=Messages.SUCCESS_CONFIGURATION_IMPORT.value, foreground="green")
            self.view.set_entry_text(self.view.column_entry, selected_plate_config.columns)
            self.view.set_entry_text(self.view.row_entry, selected_plate_config.rows)
            self.view.set_entry_text(self.view.column_spacing_entry, selected_plate_config.x_spacing)
            self.view.set_entry_text(self.view.row_spacing_entry, selected_plate_config.y_spacing)
            self.view.set_entry_text(self.view.fw_path_entry, selected_firmware_config.path.split("/")[-1])
            self.view.set_entry_text(self.view.fw_type_entry, selected_firmware_config.type.value)
            self.view.set_entry_text(self.view.fw_led_current_entry, format_range(selected_firmware_config.led_current_mode1))
            self.view.set_entry_text(self.view.fw_led_current_mode2_entry, format_range(selected_firmware_config.led_current_mode2))
            self.view.set_entry_text(self.view.fw_button_led_voltage_entry, format_range(selected_firmware_config.button_led_voltage))
            self.view.set_entry_text(self.view.fw_r_feedback_voltage_entry, format_range(selected_firmware_config.r_feedback_voltage))
            self.view.set_entry_text(self.view.fw_button_change_duration_entry, str(selected_firmware_config.button_led_mode_change_duration))
            # hide or display second mode current
            if selected_firmware_config.type == FirmwareType.MAX_ONLY:
                self.view.fw_led_current_mode2_label.grid_forget()
                self.view.fw_led_current_mode2_entry.grid_forget()
            else:
                self.view.fw_led_current_mode2_label.grid(row=3, column=0, padx=PADX, pady=PADY, sticky="nsew")
                self.view.fw_led_current_mode2_entry.grid(row=3, column=1, padx=PADX, pady=PADY, sticky="nsew")

            # update automatic cycle frame
            self.view.automatic_cycle_frame.plot_square_matrices(selected_plate_config.columns, selected_plate_config.rows)
            # bind canvas callbacks
            for x, y in self.view.cycle_rectangles.keys():
                self.view.bind_canvas_click_cb(x, y, self.evt_show_dps_info_dialog)

            self.set_view_state()
            logging.info(f"[GUI]: New configuration file has been uploaded {config}")
        except Exception as e:
            print(e)
            # update view
            self.view.upload_message.config(text=Messages.ERROR_CONFIGURATION_PARSING.value, foreground="red")
            self.set_view_state()
            return

    def evt_start_clicked(self) -> None:
        logging.debug("[GUI]: Start button has been clicked")
        # update model (external)
        start_pos_x = int(self.view.start_from_x_entry.get())
        start_pos_y = int(self.view.start_from_y_entry.get())
        self.model.set_external_state(self.model.external.set_in_automatic_cycle, start_pos_x, start_pos_y)

        # update view
        # set all metrices to grey
        self.view.automatic_cycle_frame.reset_color_of_matrices("grey")
        # clear the text area
        self.view.error_log.delete(1.0, END)
        self.set_view_state()

    def evt_pause_clicked(self) -> None:
        logging.debug("[GUI]: Pause button has been clicked")
        # update model (external)
        self.model.set_external_state(self.model.external.set_paused_in_automatic_cycle)
        # update view
        self.set_view_state()

    def evt_resume_clicked(self) -> None:
        logging.debug("[GUI]: Resume button has been clicked")
        # update model (external)
        self.model.set_external_state(self.model.external.set_resume_automatic_cycle)
        # update view
        self.set_view_state()

    def evt_finish_clicked(self) -> None:
        logging.debug("[GUI]: Finish button has been clicked")
        # update model (external)
        self.model.set_external_state(self.model.external.set_finish_automatic_cycle)
        # update view
        # set all metrices to grey
        self.view.automatic_cycle_frame.reset_color_of_matrices("grey")
        # clear the text area
        self.view.clear_tx_text(self.view.error_log)
        self.set_view_state()

    def evt_set_home_clicked(self) -> None:
        logging.debug("[GUI]: Set Home button has been clicked")
        # update model and external
        self.model.home_set = True
        self.model.set_external_state(self.model.external.set_home)
        # update view
        self.set_view_state()

    def evt_go_home_clicked(self) -> None:
        logging.debug("[GUI]: Go Home button has been clicked")
        # update model (external)
        self.model.set_external_state(self.model.external.set_moving_home)
        # update view
        self.set_view_state()

    def evt_stop_clicked(self) -> None:
        logging.debug("[GUI]: Stop button has been clicked")
        # update model (external)
        self.model.set_external_state(self.model.external.set_stop)
        # update view
        self.set_view_state()

    def evt_move_axis_clicked(self, axis: Axis) -> None:
        logging.debug(f"[GUI]: Axis button {axis.name} has been clicked")
        # update model
        self.model.selected_move_axis = axis
        # update view
        self.set_view_state()

    def evt_move_distance_clicked(self, step: int) -> None:
        axis: Axis = self.model.selected_move_axis
        current_pos_z: float = self.model.external_pos[Axis.Z.value]

        # move in X/Y axis and current position in Z is less than the safe height  or
        # move in Z axis and current position + step is less than 0
        if (self.model.home_set and
                ((current_pos_z < self.model.external_config.z_minimum_safe_height_mm and (axis == Axis.X or axis == Axis.Y)) or (current_pos_z + step < 0))):
            if not self.evt_show_confirmation_dialog():
                return

        # update model (external)
        self.model.set_external_state(self.model.external.set_moving, axis, step)
        # update view
        self.set_view_state()

    def ex_evt_update_current_pos(self, current_pos_x: int, current_pos_y: int) -> None:
        # do not set position when home is not set
        if not self.model.home_set:
            return
        if current_pos_x is not None and current_pos_y is not None:
            self.view.cycle_rectangles[current_pos_x, current_pos_y].config(bg="white")
            self.view.current_pos_label.config(text=GUIView.CURRENT_POS_TEXT.replace("{value}", f"[{current_pos_x},{current_pos_y}]"))

    def ex_evt_update_current_pos_mm(self, current_pos_mm: [float, float, float]) -> None:
        current_pos_mm_text: str = GUIView.CURRENT_POS_TEXT_MM.replace("{value}", f"[{current_pos_mm[0]:.0f},{current_pos_mm[1]:.0f},{current_pos_mm[2]:.0f}]")
        self.view.current_pos_label_mm.config(text=current_pos_mm_text)
        self.view.manual_current_pos_label_mm.config(text=current_pos_mm_text)

    def ex_evt_update_state(self, state: CNCRunnerState) -> None:
        pass
        # self.view.state_label.config(text=state.name)

    def ex_evt_process_completed(self) -> None:
        logging.info("[GUI]: EVT process completed")
        self.set_view_state()

    def ex_evt_automatic_cycle_completed(self) -> None:
        logging.info("[GUI]: Programming completed")
        self.set_view_state()

    def ex_evt_update_dps_log(self, dps_log: DPSLog) -> None:
        logging.info("[GUI]: EVT DPS updated")
        # update view
        color: str = "green" if dps_log.operation_successful else "red"
        self.view.cycle_rectangles[dps_log.x, dps_log.y].config(bg=color)
        if not dps_log.operation_successful:
            self.view.set_tx_text(self.view.error_log, MessagesFormatter.format_dps_error_msg(self.model.selected_firmware_config, dps_log))

    def evt_show_dps_info_dialog(self, x: int, y: int) -> None:
        dps_log: DPSLog = self.model.dps_log(x, y)
        if not dps_log: return

        if dps_log.operation_successful:
            message = MessagesFormatter.format_dps_ok_msg(self.model.selected_firmware_config, dps_log)
            messagebox.showinfo(f"Pozice [{x},{y}] Výstup programátoru", message)
        else:
            message = MessagesFormatter.format_dps_error_msg(self.model.selected_firmware_config, dps_log)
            messagebox.showerror(f"Pozice [{x},{y}] Chybový výstup programátoru", message)

    def evt_show_confirmation_dialog(self) -> bool:
        return messagebox.askyesno(title="Potvrzení operace", message="Potenciálně nebezpečná operace - hrozí poškození. Opravdu chcete pokračovat?")


    #region GUI STATE setters
    def set_view_state(self) -> None:
        self.set_settings_frame_view_state()
        self.set_manual_mode_frame_view_state()
        self.set_automatic_cycle_frame_state()

    def set_manual_mode_frame_view_state(self) -> None:
        state = self.model.external_state

        go_home_button_enabled: bool = self.model.home_set and state == CNCRunnerState.STOPPED
        set_home_button_enabled: bool = self.model.external_state == CNCRunnerState.STOPPED
        stop_button_enabled: bool = state == CNCRunnerState.MOVING_HOME or state == CNCRunnerState.MOVING_BY_STEP
        move_buttons_enabled = self.model.external_state == CNCRunnerState.STOPPED

        self.view.set_button_state(self.view.go_home_button, go_home_button_enabled)
        self.view.set_button_state(self.view.set_home_button, set_home_button_enabled)
        self.view.set_button_state(self.view.manual_stop_button, stop_button_enabled)

        #TODO: simplify
        for axis in Axis:
            self.view.move_axis_buttons[axis.value].config(style="Accent.TButton" if self.model.selected_move_axis == axis else "TButton", state=tk.NORMAL if move_buttons_enabled else tk.DISABLED)

        for step in GUIView.STEPS:
            self.view.set_button_state(self.view.move_distance_buttons[step], move_buttons_enabled, False)
            self.view.set_button_state(self.view.move_distance_buttons[-step], move_buttons_enabled, False)

    def set_automatic_cycle_frame_state(self) -> None:
        state = self.model.external_state

        start_button_enabled: bool = (
                self.model.external_config is not None and
                self.model.home_set and
                state == CNCRunnerState.STOPPED
        )
        pause_button_enabled: bool = state == CNCRunnerState.IN_AUTOMATIC_CYCLE
        resume_button_enabled: bool = state == CNCRunnerState.PAUSED_IN_AUTOMATIC_CYCLE and self.model.external.next_position_in_sequence() is not None
        finish_button_enabled: bool = state == CNCRunnerState.PAUSED_IN_AUTOMATIC_CYCLE or state == CNCRunnerState.COMPLETED_AUTOMATIC_CYCLE

        # automatic cycle
        self.view.set_button_state(self.view.start_button, start_button_enabled)
        self.view.set_button_state(self.view.pause_button, pause_button_enabled)
        self.view.set_button_state(self.view.resume_button, resume_button_enabled)
        self.view.set_button_state(self.view.finish_button, finish_button_enabled)
        self.view.set_entry_state(self.view.start_from_x_entry, start_button_enabled)
        self.view.set_entry_state(self.view.start_from_y_entry, start_button_enabled)
        self.view.set_tx_state(self.view.error_log, False)

    def set_settings_frame_view_state(self) -> None:
        browse_files_button_enabled: bool = self.model.external_state == CNCRunnerState.STOPPED
        upload_button_enabled: bool = (self.model.selected_config_path != '' and
                                       self.model.selected_config_path != self.model.uploaded_config_path and
                                       self.model.external_state == CNCRunnerState.STOPPED)
        plate_config_enabled: bool = False

        self.view.set_button_state(self.view.browse_files_button, browse_files_button_enabled)
        self.view.set_button_state(self.view.upload_button, upload_button_enabled)
        self.view.set_entry_state(self.view.config_entry, plate_config_enabled)

        self.view.set_entry_state(self.view.column_entry, plate_config_enabled)
        self.view.set_entry_state(self.view.row_entry, plate_config_enabled)
        self.view.set_entry_state(self.view.column_spacing_entry, plate_config_enabled)
        self.view.set_entry_state(self.view.row_spacing_entry, plate_config_enabled)
        self.view.set_entry_state(self.view.fw_path_entry, plate_config_enabled)
        self.view.set_entry_state(self.view.fw_type_entry, plate_config_enabled)
        self.view.set_entry_state(self.view.fw_led_current_entry, plate_config_enabled)
        self.view.set_entry_state(self.view.fw_led_current_mode2_entry, plate_config_enabled)
        self.view.set_entry_state(self.view.fw_button_change_duration_entry, plate_config_enabled)
        self.view.set_entry_state(self.view.fw_r_feedback_voltage_entry, plate_config_enabled)
        self.view.set_entry_state(self.view.fw_button_change_duration_entry, plate_config_enabled)

    #endregion GUI STATE

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)

    root = create_root_window()
    view = GUIView(root)
    view.pack(fill=tk.BOTH, expand=1)

    controller = GUIController(view, None)
    view.set_controller(controller)

    root.update()
    root.mainloop()

