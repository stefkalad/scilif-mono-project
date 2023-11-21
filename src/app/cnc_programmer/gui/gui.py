from __future__ import annotations

import logging
import os
import tkinter as tk
from enum import Enum
from tkinter import DISABLED, NORMAL, ttk, messagebox, END
from tkinter import filedialog
from typing import Callable

from app.cnc_programmer.config.config import CNCProgrammerConfig
from app.cnc_programmer.config.config_parser import CNCProgrammerConfigParser
from app.cnc_programmer.config.firmware import FirmwareConfig
from app.cnc_programmer.config.plate import PlateConfig
from app.cnc_programmer.dps_log import DPSLog
from app.cnc_programmer.gui.scrollable_frame import ScrollableFrame
from app.cnc_programmer.stepper.position import Axis
from app.cnc_programmer.stepper.state import CNCRunnerState

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

#TODO: update Matrices

class Messages(Enum):
    ERROR_CONFIGURATION_SELECTION = "Žádná konfigurace nebyla vybrána!"
    ERROR_CONFIGURATION_PARSING = "Chyba v konfiguraci!"
    SUCCESS_CONFIGURATION_IMPORT = "Konfigurace byla úspěšně nahrána!"


class GUIModel:
    def __init__(self, external: "CNCRunner") -> None:
        self.external = external

        # helper
        self.config_path: str = ''
        self.selected_plate_config_name: str = ''
        self.selected_firmware_config_name: str = ''
        self.selected_move_axis: int = Axis.X.value

        # stateful
        self.home_set: bool = False
        self.manual_move_mode_set: bool = True

    @property
    def external_config(self) -> CNCProgrammerConfig | None:
        if self.external is not None:
            return self.external.config
        else:
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
            return None

    @selected_plate_config.setter
    def selected_plate_config(self, config: PlateConfig) -> None:
        if self.external is not None:
            self.external.set_selected_plate_config(config)
        else:
            logging.error("External CNC runner is not defined!")

    @property
    def selected_firmware_config(self) -> FirmwareConfig | None:
        if self.external is not None:
            return self.external.selected_firmware_config
        else:
            return None

    @selected_firmware_config.setter
    def selected_firmware_config(self, config: FirmwareConfig) -> None:
        if self.external is not None:
            self.external.set_selected_firmware_config(config)
        else:
            logging.error("External CNC runner is not defined!")

    @property
    def external_state(self) -> CNCRunnerState | None:
        if self.external is not None:
            return self.external.state
        else:
            return None
    @property
    def external_dps_to_go(self) -> bool | None:
        if self.external is not None:
            if len(self.external.dps_logs.keys()) > 0:
                return len(self.external.dps_logs.keys()) != self.selected_plate_config.columns * self.selected_plate_config.rows
            return False

        else:
            return None

    def set_cycle(self, start_from_x: int, start_from_y: int) -> None:
        if self.external is not None:
            self.external.set_cycle(start_from_x, start_from_y)
        else:
            logging.error("External CNC runner is not defined!")

    def set_moving(self, axis: int, step_mm: float) -> None:
        if self.external is not None:
            self.external.set_moving(axis, step_mm)
        else:
            logging.error("External CNC runner is not defined!")

    def set_go_home(self) -> None:
        if self.external is not None:
            self.external.set_go_home()
        else:
            logging.error("External CNC runner is not defined!")

    def set_stop(self) -> None:
        if self.external is not None:
            self.external.set_stop()
        else:
            logging.error("External CNC runner is not defined!")

    def set_resume(self) -> None:
        if self.external is not None:
            pos_keys = self.external.dps_logs.keys()
            max_pos_y = max(pos_keys, key=lambda pos: pos[1])[1]
            max_pos_y_x = filter(lambda pos: pos[1] == max_pos_y, pos_keys)
            max_pos_x = max(max_pos_y_x, key=lambda pos: pos[0])[0] if max_pos_y % 2 == 0 else min(max_pos_y_x, key=lambda pos: pos[0])[0]
            self.set_cycle(max_pos_x, max_pos_y)
        else:
            logging.error("External CNC runner is not defined!")

    def dps_log(self, x: int, y: int) -> DPSLog:
        if self.external is not None:
            return self.external.dps_logs[x, y]
        else:
            logging.error("External CNC runner is not defined!")


class GUIController:
    AXIS = ["X", "Y", "Z"]
    STEPS = [20, 10, 5, 1]

    def __init__(self, view: GUIView, external: "CNCRunner"):
        self.model: GUIModel = GUIModel(external)
        self.view: GUIView = view

        # bind callbacks
        self.bind_callbacks()
        # initial setup
        self.init()


    def bind_callbacks(self) -> None:
        self.view.bind_close_window_cb(self.destroy)
        self.view.bind_button_click_cb(self.view.browse_files_button, self.evt_browse_files_clicked)
        self.view.bind_button_click_cb(self.view.upload_button, self.evt_upload_config_clicked)
        self.view.bind_button_click_cb(self.view.start_button, self.evt_start_clicked)
        self.view.bind_button_click_cb(self.view.stop_button, self.evt_stop_clicked)
        self.view.bind_button_click_cb(self.view.resume_button, self.evt_resume_clicked)
        self.view.bind_button_click_cb(self.view.go_home_button, self.evt_go_home_clicked)
        self.view.bind_button_click_cb(self.view.set_home_button, self.evt_set_home_clicked)


        # bind move buttons
        self.view.bind_button_click_cb(self.view.move_button, self.evt_move_clicked)
        for axis in range(len(GUIController.AXIS)):
            self.view.bind_button_click_cb(self.view.move_axis_buttons[axis], lambda _axis=axis: self.evt_move_axis_clicked(_axis))
        for step in GUIController.STEPS:
            self.view.bind_button_click_cb(self.view.move_distance_buttons[step], lambda _step=step: self.evt_move_distance_clicked(_step))
            self.view.bind_button_click_cb(self.view.move_distance_buttons[-step], lambda _step=-step: self.evt_move_distance_clicked(_step))

        # bind canvas
        for x, y in self.view.rectangles.keys():
            self.view.bind_canvas_click_cb(x, y, self.evt_show_dialog)

    def init(self) -> None:
        # default text
        self.view.set_entry_text(self.view.start_from_x_entry, str(0))
        self.view.set_entry_text(self.view.start_from_y_entry, str(0))
        # buttons default style
        self.view.upload_button.config(style="Accent.TButton")
        self.view.browse_files_button.config(style="Accent.TButton")
        self.view.move_button.config(style="Accent.TButton")
        self.view.set_home_button.config(style="Accent.TButton")
        # load default config
        default_config_path: str = f"{ROOT_DIR}/../resources/config_cnc_programmer.conf"
        self.view.config_entry_text.set(default_config_path)
        self.model.config_path = default_config_path
        self.evt_upload_config_clicked()


    def destroy(self):
        logging.info("[EVT]: Stopping application")
        self.view.root.destroy()
        if self.model.external is not None:
            self.model.external.stop()

    def evt_show_dialog(self, x, y) -> None:
        dps_log = self.model.dps_log(x, y)
        if not dps_log: return

        messagebox.showinfo(f"OK [{x},{y}]" if dps_log.operation_successful else f"ERROR [{x},{y}]",
                            self._format_dps_ok_msg(dps_log) if dps_log.operation_successful else self._format_dps_error_msg(dps_log))

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
        self.model.config_path = file_path
        # update view
        self.view.config_entry_text.set(file_path)
        self.set_view_state()
        logging.info(f"[GUI]: New configuration file path has been selected {file_path}")

    def evt_upload_config_clicked(self) -> None:
        try:
            config = CNCProgrammerConfigParser(self.model.config_path).parse_config()
            # update model (external)
            selected_firmware_config = list(config.firmware_configs.values())[0]
            selected_plate_config = list(config.plate_configs.values())[0]
            self.model.external_config = config
            self.model.selected_plate_config = selected_plate_config
            self.model.selected_firmware_config = selected_firmware_config
            # update view
            self.view.upload_message.config(text=Messages.SUCCESS_CONFIGURATION_IMPORT.value, foreground="green")
            self.view.set_entry_text(self.view.column_entry, selected_plate_config.columns)
            self.view.set_entry_text(self.view.row_entry, selected_plate_config.rows)
            self.view.set_entry_text(self.view.column_spacing_entry, selected_plate_config.x_spacing)
            self.view.set_entry_text(self.view.row_spacing_entry, selected_plate_config.y_spacing)
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
        self.model.set_cycle(start_pos_x, start_pos_y)

        # update view
        # clear the text area
        self.view.error_log.insert(1.0, END)
        # set all rectangels to grey
        for rectangle in self.view.rectangles.values():
            rectangle.config(bg="grey")
        self.set_view_state()

    def evt_stop_clicked(self) -> None:
        logging.debug("[GUI]: Stop button has been clicked")
        # update model (external)
        self.model.set_stop()
        # update view
        self.set_view_state()

    def evt_resume_clicked(self) -> None:
        logging.debug("[GUI]: Resume button has been clicked")
        # update model (external)
        self.model.set_resume()
        # update view
        self.set_view_state()

    def evt_set_home_clicked(self) -> None:
        logging.debug("[GUI]: Set Home button has been clicked")
        # update model and external
        self.model.home_set = True
        self.model.external.set_home()
        # update view
        self.set_view_state()

    def evt_go_home_clicked(self) -> None:
        logging.debug("[GUI]: Go Home button has been clicked")
        # update model (external)
        self.model.set_go_home()
        # update view
        self.set_view_state()

    def evt_move_clicked(self) -> None:
        logging.debug("[GUI]: Move button has been clicked")
        # update model
        self.model.manual_move_mode_set = not self.model.manual_move_mode_set
        # update view
        self.set_view_state()
        self.view.move_axis_buttons[self.model.selected_move_axis].config(style="Accent.TButton")

    def evt_move_axis_clicked(self, axis: int) -> None:
        # update model
        self.model.selected_move_axis = axis
        # update view
        self.set_view_state()

    def evt_move_distance_clicked(self, step: int) -> None:
        # update model
        self.model.set_moving(self.model.selected_move_axis, step)
        # update view
        self.set_view_state()

    def ex_evt_update_current_pos(self, current_pos_x: int, current_pos_y: int) -> None:
        # do not set position when home is not set
        if not self.model.home_set:
            return
        if current_pos_x is not None and current_pos_y is not None:
            self.view.rectangles[current_pos_x, current_pos_y].config(bg="white")
            self.view.current_pos_label.config(text=GUIView.CURRENT_POS_TEXT.replace("{value}", f"[{current_pos_x},{current_pos_y}]"))

    def ex_evt_update_current_pos_mm(self, current_pos_mm: [float, float, float]) -> None:
        # do not set position when home is not set
        if not self.model.home_set:
            return
        self.view.current_pos_label_mm.config(text=GUIView.CURRENT_POS_TEXT_MM.replace("{value}", f"[{current_pos_mm[0]:.0f},{current_pos_mm[1]:.0f},{current_pos_mm[2]:.0f}]"))

    def ex_evt_update_dps_log(self, dps_log: DPSLog) -> None:
        color: str = "green" if dps_log.operation_successful else "red"
        self.view.rectangles[dps_log.x, dps_log.y].config(bg=color)
        if not dps_log.operation_successful:
            self.view.error_log.insert(END, self._format_dps_error_msg(dps_log))

    def ex_evt_process_completed(self) -> None:
        logging.info("[GUI]: EVT process completed")
        self.set_view_state()

    def ex_evt_automatic_cycle_completed(self) -> None:
        logging.info("[GUI]: Programming completed")
        #TODO: show button


    def _format_dps_ok_msg(self, dps_log: DPSLog) -> str:
        return (f"[programování]: FW: {self.model.external_config.firmware_default_path}, výstup: {dps_log.fw_upload_message}\n" +
                f"[testování] Proud LED (mód 1): {dps_log.led_current_mode1} mA\n" +
                f"[testování] Napětí LED tlačítka:  {dps_log.button_led_voltage} mV\n")

    def _format_dps_error_msg(self, dps_log: DPSLog) -> str:
        if not dps_log.fw_uploaded:
            return self._format_fw_upload_error_msg(dps_log)
        else:
            message: str = ''
            if not dps_log.led_current_mode1_passed:
                message += self._format_led_current_error_msg(dps_log, self.model.selected_firmware_config.led_current_mode1, 1)
            # if not dps_log.led_current_mode2_passed:
            #     message += self._format_led_current_error_msg(dps_log, self.model.selected_firmware_config.led_current_mode2, 2)
            if not dps_log.button_led_voltage_passed:
                message += self._format_button_led_voltage_error_msg(dps_log, self.model.selected_firmware_config.button_led_voltage)
            return message

    def _format_fw_upload_error_msg(self, dps_log: DPSLog) -> str:
        return f"ERROR [{dps_log.x},{dps_log.y}][programování]: {dps_log.fw_upload_message}\n"

    def _format_led_current_error_msg(self, dps_log: DPSLog, spec: (int, int), mode: int = 1) -> str:
        led_current = dps_log.led_current_mode1 if mode == 1 else dps_log.led_current_mode2
        return f"ERROR [{dps_log.x},{dps_log.y}] [testování]: proud LED (mód {mode}) mimo specifikaci {led_current:.0f} mA x ({spec[0]},{spec[1]}) mA\n"

    def _format_button_led_voltage_error_msg(self, dps_log: DPSLog, spec: (int, int)) -> str:
        return f"ERROR [{dps_log.x},{dps_log.y}] [testování]: napětí LED tlačítka mimo specifikaci {dps_log.button_led_voltage:.0f} mV x ({spec[0]}, {spec[1]}) mV\n"

    def set_view_state(self) -> None:
        self.set_view_config_buttons_and_entries_state()
        self.set_view_action_buttons_and_entries_state()
        self.set_view_frame_state()

    def set_view_action_buttons_and_entries_state(self) -> None:
        start_button_enabled: bool = (
                self.model.external_config is not None and
                self.model.home_set and
                not self.model.manual_move_mode_set and
                self.model.external_state == CNCRunnerState.STOPPED
        )
        stop_button_enabled: bool = not (self.model.external_state == CNCRunnerState.STOPPED)
        resume_button_enabled: bool = (
                self.model.external_config is not None and
                self.model.home_set and
                not self.model.manual_move_mode_set and
                self.model.external_state == CNCRunnerState.STOPPED and
                self.model.external_dps_to_go
        )
        move_button_enabled: bool = self.model.external_state == CNCRunnerState.STOPPED
        go_home_button_enabled: bool = self.model.home_set and self.model.external_state == CNCRunnerState.STOPPED
        set_home_button_enabled: bool = self.model.external_state == CNCRunnerState.STOPPED
        from_entry_enabled: bool = start_button_enabled
        move_axisstep_buttons_enabled = self.model.external_state == CNCRunnerState.STOPPED

        self.view.set_button_state(self.view.start_button, start_button_enabled)
        self.view.set_button_state(self.view.stop_button, stop_button_enabled)
        self.view.set_button_state(self.view.resume_button, resume_button_enabled)
        self.view.set_button_state(self.view.go_home_button, go_home_button_enabled)
        self.view.set_button_state(self.view.set_home_button, set_home_button_enabled)
        self.view.set_entry_state(self.view.start_from_x_entry, from_entry_enabled)
        self.view.set_entry_state(self.view.start_from_y_entry, from_entry_enabled)

        self.view.set_button_state(self.view.move_button, move_button_enabled)

        for i in range(len(GUIController.AXIS)):
            self.view.move_axis_buttons[i].config(style="Accent.TButton" if self.model.selected_move_axis == i else "TButton", state=NORMAL if move_axisstep_buttons_enabled else DISABLED)

        for step in GUIController.STEPS:
            self.view.set_button_state(self.view.move_distance_buttons[step], move_axisstep_buttons_enabled, False)
            self.view.set_button_state(self.view.move_distance_buttons[-step], move_axisstep_buttons_enabled, False)

    def set_view_config_buttons_and_entries_state(self) -> None:
        browse_files_button_enabled: bool = True
        upload_button_enabled: bool = self.model.config_path != ''
        plate_config_enabled: bool = False

        self.view.set_button_state(self.view.browse_files_button, browse_files_button_enabled)
        self.view.set_button_state(self.view.upload_button, upload_button_enabled)
        self.view.set_entry_state(self.view.column_entry, plate_config_enabled)
        self.view.set_entry_state(self.view.row_entry, plate_config_enabled)
        self.view.set_entry_state(self.view.column_spacing_entry, plate_config_enabled)
        self.view.set_entry_state(self.view.row_spacing_entry, plate_config_enabled)

        self.view.move_button.config(text="Vypni manuální mód" if self.model.manual_move_mode_set else "Manuální mód")

    def set_view_frame_state(self) -> None:
        config_frame_visible: bool = self.model.external_state != CNCRunnerState.AUTOMATIC_CYCLE
        # config_frame_visible: bool = True
        matrix_error_log_frame_visible: bool = self.model.external_state == CNCRunnerState.AUTOMATIC_CYCLE and not self.model.manual_move_mode_set
        move_frame_visible: bool = self.model.manual_move_mode_set

        if config_frame_visible:
            self.view.config_frame.grid(row=GUIView.CONFIG_FRAME_ROW, column=0, padx=GUIView.PADX, pady=GUIView.PADY, sticky="nsew")
            self.view.plate_config_frame.grid(row=GUIView.PLATE_CONFIG_FRAME_ROW, column=0, padx=GUIView.PADX, pady=GUIView.PADY, sticky="nsew")
        else:
            self.view.config_frame.grid_forget()
            self.view.plate_config_frame.grid_forget()

        if matrix_error_log_frame_visible:
            self.view.matrix_frame.grid(row=0, column=0, columnspan=2, padx=GUIView.PADX, pady=GUIView.PADY, sticky="nsew")
            self.view.error_log_frame.grid(row=0, column=3, columnspan=2, padx=GUIView.PADX, pady=GUIView.PADY, sticky="nsew")
        else:
            self.view.matrix_frame.grid_forget()
            self.view.error_log_frame.grid_forget()

        if move_frame_visible:
            self.view.move_frame.grid(row=1, column=0, columnspan=5, padx=GUIView.PADX, pady=GUIView.PADY, sticky="nsew")
        else:
            self.view.move_frame.grid_forget()


class GUIView(ttk.Frame):
    FG_COLOR = "#eaf205"
    MEDIUM_FONT = 12

    SMALL_PADX = (5, 5)
    SMALL_PADY = (7.5, 7.5)
    PADX = (10, 10)
    PADY = (10, 10)
    DPS_HEIGHT_PX: int = 50
    DPS_WIDTH_PX: int = 100
    MIN_SIZE_PX: int = 1300

    CONFIG_FRAME_ROW = 1
    PLATE_CONFIG_FRAME_ROW = 2
    APPLICATION_FRAME_ROW = 3

    CURRENT_POS_TEXT_MM = "Současná pozice [x,y,z] [mm]: {value}"
    CURRENT_POS_TEXT = "Současná pozice [x,y]: {value}"



    def __init__(self, root: tk.Tk, parent_frame: ScrollableFrame):
        super().__init__(parent_frame)
        self.root = root
        self.parent_frame = parent_frame

        self.grid(row=0, column=0, sticky='ns')

        self.rectangles: dict[(int, int), tk.Canvas] = {}
        self.move_axis_buttons: dict[int, ttk.Button] = {}
        self.move_distance_buttons: dict[int, ttk.Button] = {}

        self.label = ttk.Label(self, text="SCILIF CNC Programátor", justify="center", font=("-size", 18, "-weight", "bold"))
        self.label.grid(row=0, column=0, sticky="ns")

        self.config_frame = ttk.LabelFrame(self, text="Výběr Konfigurace")
        self.config_frame.grid(row=GUIView.CONFIG_FRAME_ROW, column=0, padx=GUIView.SMALL_PADX, pady=GUIView.SMALL_PADY, sticky="nsew")
        self._create_configuration_frame_widgets()

        self.plate_config_frame = ttk.LabelFrame(self, text="Nastavení Desky & Firmware")
        self.plate_config_frame.grid(row=GUIView.PLATE_CONFIG_FRAME_ROW, column=0, padx=GUIView.SMALL_PADX, pady=GUIView.SMALL_PADY, sticky="nsew")
        self._create_plate_config_frame_widgets()

        self.application_frame = ttk.LabelFrame(self, text="Kontrolní Panel")
        self.application_frame.grid(row=GUIView.APPLICATION_FRAME_ROW, column=0, padx=GUIView.SMALL_PADX, pady=GUIView.SMALL_PADY, sticky="nsew")
        self._create_application_frame_widgets()

    def set_controller(self, controller: GUIController):
        self.controller = controller

    def _create_configuration_frame_widgets(self) -> None:
        COLUMN_WEIGHTS = [0, 1, 0]

        self.config_label = ttk.Label(self.config_frame, text="Konfigurační soubor:")
        self.config_label.grid(row=0, column=0, padx=GUIView.PADX, pady=GUIView.PADY, sticky="nsew")

        self.config_entry_text = tk.StringVar()
        self.config_entry = ttk.Entry(self.config_frame, textvariable=self.config_entry_text, state=DISABLED)
        self.config_entry.grid(row=0, column=1, columnspan=2, padx=GUIView.PADX, pady=GUIView.PADY, sticky="nsew")

        self.browse_files_button = ttk.Button(self.config_frame, text="Procházet")
        self.browse_files_button.grid(row=0, column=3, padx=10, pady=10, sticky="nsew")

        self.upload_button = ttk.Button(self.config_frame, text="Nahrát")
        self.upload_button.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        self.upload_message = ttk.Label(self.config_frame, text="", anchor="center")
        self.upload_message.grid(row=2, columnspan=3, padx=10, pady=10, sticky="ew")

        for index, weight in enumerate(COLUMN_WEIGHTS):
            self.config_frame.columnconfigure(index, weight=weight)

    def _create_plate_config_frame_widgets(self):
        COLUMN_WEIGHTS = [2, 1, 2, 1]

        self.column_label, self.column_entry = self._generate_label_entry_pair(self.plate_config_frame, "Sloupce (N):", 0, 0, GUIView.PADX, GUIView.SMALL_PADY)
        self.row_label, self.row_entry = self._generate_label_entry_pair(self.plate_config_frame, "Řádky (M):", 0, 2, GUIView.PADX, GUIView.SMALL_PADY)

        self.column_spacing_label, self.column_spacing_entry = self._generate_label_entry_pair(self.plate_config_frame, "Rozteč (X) [mm]:", 1, 0, GUIView.PADX, GUIView.SMALL_PADY)
        self.row_spacing_label, self.row_spacing_entry = self._generate_label_entry_pair(self.plate_config_frame, "Rozteč (Y) [mm]:", 1, 2, GUIView.PADX, GUIView.SMALL_PADY)

        # self.column_offset_label, self.column_offset_entry = self._generate_label_entry_pair(self.plate_config_frame, "Offset (X) of first DPS [mm]:", 2, 0, GUIView.PADX, GUIView.SMALL_PADY)
        # self.row_offset_label, self.row_offset_entry = self._generate_label_entry_pair(self.plate_config_frame, "Offset (Y) of first DPS [mm]:", 2, 2, GUIView.PADX, GUIView.SMALL_PADY)

        for index, weight in enumerate(COLUMN_WEIGHTS):
            self.plate_config_frame.columnconfigure(index, weight=weight)

    def _create_application_frame_widgets(self):
        COLUMN_WEIGHTS = [1, 1, 1, 1, 1]

        self.start_button = ttk.Button(self.application_frame, text="Start")
        self.start_button.grid(row=0, column=0, padx=GUIView.PADX, pady=GUIView.PADY, sticky="nsew")

        label = ttk.Label(self.application_frame, text="Z pozice X:")
        label.grid(row=0, column=1, padx=GUIView.PADX, pady=GUIView.PADY, sticky="e")
        self.start_from_x_entry = ttk.Entry(self.application_frame, width=10)
        self.start_from_x_entry.grid(row=0, column=2, padx=GUIView.PADX, pady=GUIView.PADY, sticky="w")

        label = ttk.Label(self.application_frame, text="Z pozice Y:")
        label.grid(row=0, column=3, padx=GUIView.PADX, pady=GUIView.PADY, sticky="e")
        self.start_from_y_entry = ttk.Entry(self.application_frame, width=10)
        self.start_from_y_entry.grid(row=0, column=4, padx=GUIView.PADX, pady=GUIView.PADY, sticky="w")

        self.stop_button = ttk.Button(self.application_frame, text="Stop")
        self.stop_button.grid(row=1, column=0, padx=GUIView.PADX, pady=GUIView.PADY, sticky="nsew")
        self.resume_button = ttk.Button(self.application_frame, text="Pokračovat")
        self.resume_button.grid(row=1, column=1, padx=GUIView.PADX, pady=GUIView.PADY, sticky="nsew")

        self.move_button = ttk.Button(self.application_frame, text="Manuální Mód")
        self.move_button.grid(row=1, column=2, padx=GUIView.PADX, pady=GUIView.PADY, sticky="nsew")
        self.set_home_button = ttk.Button(self.application_frame, text="Nastavit Základnu")
        self.set_home_button.grid(row=1, column=3, padx=GUIView.PADX, pady=GUIView.PADY, sticky="nsew")
        self.go_home_button = ttk.Button(self.application_frame, text="Do Základny")
        self.go_home_button.grid(row=1, column=4, padx=GUIView.PADX, pady=GUIView.PADY, sticky="nsew")

        self.current_pos_label = ttk.Label(self.application_frame, text="Současná pozice: ?", font=("-size", GUIView.MEDIUM_FONT, "-weight", "bold"))
        self.current_pos_label.grid(row=2, column=0, columnspan=2, padx=GUIView.PADX, pady=GUIView.PADY, sticky="nsew")
        self.current_pos_label_mm = ttk.Label(self.application_frame, text="Současná pozice [mm]: ?",  font=("-size", GUIView.MEDIUM_FONT, "-weight", "bold"))
        self.current_pos_label_mm.grid(row=2, column=2, columnspan=2, padx=GUIView.PADX, pady=GUIView.PADY, sticky="nsew")

        for index, weight in enumerate(COLUMN_WEIGHTS):
            self.application_frame.columnconfigure(index, weight=weight)

        self.application_frame_content = tk.Frame(self.application_frame)
        self.application_frame_content.grid(row=3, column=0, columnspan=5, padx=GUIView.PADX, pady=GUIView.PADY, sticky="nsew")

        self._create_application_frame_matrix_error_log_widgets()
        self._create_application_frame_move_widgets()

    def _create_application_frame_matrix_error_log_widgets(self):

        # COLUMN_WEIGHTS = [2, 1]

        self.matrix_frame = ttk.Frame(self.application_frame_content, width=200)
        self.matrix_frame.grid(row=0, column=0, columnspan=2, padx=GUIView.PADX, pady=GUIView.PADY, sticky="nsew")
        self._create_square_matrices(self.matrix_frame, 5, 10)

        self.error_log_frame = ttk.Frame(self.application_frame_content)
        self.error_log_frame.grid(row=0, column=3, columnspan=2, padx=GUIView.PADX, pady=GUIView.PADY, sticky="nsew")

        self.error_log = tk.Text(self.error_log_frame, wrap="none", width=50)
        self.error_log.grid(row=0, column=5, sticky="nsew")
        self.error_log_scrollbar = ttk.Scrollbar(self.error_log_frame, orient="vertical", command=self.error_log.yview)
        self.error_log.config(yscrollcommand=self.error_log_scrollbar.set)
        #TODO:
        # scroll_text = lambda event: self.error_log.yview_scroll(-1 * (event.delta // 120), "units")
        # self.error_log.bind("<MouseWheel>", scroll_text)

        # for index, weight in enumerate(COLUMN_WEIGHTS):
        #     self.application_frame_content.columnconfigure(index, weight=weight)


    def _create_application_frame_move_widgets(self):
        self.move_frame = ttk.Frame(self.application_frame_content)
        #NOTE: by default under START/STOP
        self.move_frame.grid(row=1, column=0, columnspan=5, padx=GUIView.PADX, pady=GUIView.PADY, sticky="nsew")

        for i, axis in enumerate(GUIController.AXIS):
            button = ttk.Button(self.move_frame, text=axis)
            button.grid(row=0, column=i, padx=GUIView.PADX, pady=GUIView.PADY, sticky="nsew")
            self.move_axis_buttons[i] = button

        for i, step in enumerate(GUIController.STEPS):
            button = ttk.Button(self.move_frame, text=f"+{step} mm")
            button.grid(row=1, column=i * 2, padx=GUIView.SMALL_PADX, pady=GUIView.PADY, sticky="nsew")
            self.move_distance_buttons[step] = button
            button = ttk.Button(self.move_frame, text=f"-{step} mm")
            button.grid(row=1, column=i * 2 + 1, padx=GUIView.SMALL_PADX, pady=GUIView.PADY, sticky="nsew")
            self.move_distance_buttons[-step] = button

    def _create_square_matrices(self, matrix_frame: ttk.Frame, columns: int, rows: int):
        for row in range(rows):
            for column in range(columns):
                canvas = tk.Canvas(matrix_frame, width=GUIView.DPS_WIDTH_PX, height=GUIView.DPS_HEIGHT_PX, bg="grey")
                canvas.grid(row=row, column=column, sticky="nsew")
                self.rectangles[(column, rows - (row + 1))] = canvas

    def _generate_label_entry_pair(self, frame, label_text: str, row: int, column: int, padx=PADX, pady=PADY, state=NORMAL) -> (ttk.Label, ttk.Entry):
        label = ttk.Label(frame, text=label_text)
        label.grid(row=row, column=column, padx=padx, pady=pady, sticky="nsew")
        entry = ttk.Entry(frame, state=state)
        entry.grid(row=row, column=column + 1, padx=padx, pady=pady, sticky="nsew")
        return (label, entry)


    def bind_close_window_cb(self, callback):
        self.root.protocol("WM_DELETE_WINDOW", callback)
        self.parent_frame.exit_button.config(command=callback)

    def bind_button_click_cb(self, button: ttk.Button, callback) -> None:
        button.config(command=callback)

    def bind_canvas_click_cb(self, x: int, y: int, callback: Callable[[int, int], None]):
        self.rectangles[(x, y)].bind("<Button-1>", lambda evt, _x=x, _y=y: callback(_x, _y))

    def set_button_state(self, button: ttk.Button, condition: bool, change_style: bool = True) -> None:
        self.enable_button(button, change_style) if condition else self.disable_button(button)

    def enable_button(self, button: ttk.Button, change_style=True) -> None:
        if str(button["state"]) != str(NORMAL):
            logging.debug(f"[GUI]: Changing {button['text']} state to {NORMAL}")
            button.config(state=NORMAL, style="Accent.TButton" if change_style else "TButton")

    def disable_button(self, button: ttk.Button) -> None:
        if str(button["state"]) != str(DISABLED):
            logging.debug(f"[GUI]: Changing {button['text']} state to {DISABLED}")
            button.config(state=DISABLED, style="TButton")

    def set_entry_state(self, entry: ttk.Entry, condition: bool) -> None:
        self.enable_entry(entry) if condition else self.disable_entry(entry)

    def enable_entry(self, entry: ttk.Entry) -> None:
        if str(entry["state"]) != str(NORMAL):
            entry.config(state=NORMAL)

    def disable_entry(self, entry: ttk.Entry) -> None:
        if str(entry["state"]) != str(DISABLED):
            entry.config(state=DISABLED)

    def set_entry_text(self, entry: ttk.Entry, text: str) -> None:
        entry.insert(0, text)



def create_root_window() -> (tk.Tk, ttk.Frame):

    root = tk.Tk()
    root.title('SCILIF CNC PROGRAMMER')
    root.tk.call("source", f"{ROOT_DIR}/../../../lib/theme/azure.tcl")
    root.tk.call("set_theme", "dark")

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Set a minsize for the window
    # root.minsize(root.winfo_width(), root.winfo_height())
    root.maxsize(screen_width, screen_height)
    root.geometry("%dx%d+0+0" % (screen_width, screen_height - 20))

    root.bind_all('<Control-c>', lambda _: root.destroy())
    return root


if __name__ == "__main__":

    logging.getLogger().setLevel(logging.INFO)


    root = create_root_window()
    view = GUIView(root, ScrollableFrame(root))
    controller = GUIController(view, None)
    view.set_controller(controller)

    root.update()
    root.mainloop()
