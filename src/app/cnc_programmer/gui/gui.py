from __future__ import annotations

import logging
import os
import tkinter as tk
from enum import Enum
from tkinter import BOTH, BOTTOM, DISABLED, LEFT, NORMAL, RIGHT, TOP, X, Y, YES, ttk, messagebox, END
from tkinter import filedialog
from typing import Callable

from app.cnc_programmer.config.config import CNCProgrammerConfig
from app.cnc_programmer.config.config_parser import CNCProgrammerConfigParser
from app.cnc_programmer.config.firmware import FirmwareConfig
from app.cnc_programmer.config.plate import PlateConfig
from app.cnc_programmer.dps_log import DPSLog
from app.cnc_programmer.stepper.position import Axis


class Messages(Enum):
    ERROR_CONFIGURATION_SELECTION = "No configuration file was selected!"
    ERROR_CONFIGURATION_PARSING = "Error in configuration file parsing!"
    SUCCESS_CONFIGURATION_IMPORT = "Configuration was successfully imported!"


class GUIModel:
    def __init__(self, external: "CNCRunner") -> None:
        self.config_path: str = ''
        self.selected_plate_config_name: str = ''
        self.selected_firmware_config_name: str = ''
        self.external = external

        self._selected_move_axis: int = Axis.X.value

    @property
    def external_is_running(self) -> bool | None:
        if self.external is not None:
            return self.external.programming_all_plates
        else:
            return None

    @external_is_running.setter
    def external_is_running(self, value: bool) -> None:
        if self.external is not None:
            self.external.set_running(value)
        else:
            logging.error("External CNC runner is not defined!")

    @property
    def external_config(self) -> CNCProgrammerConfig | None:
        if self.external is not None:
            return self.external.external_config
        else:
            return None

    @external_config.setter
    def external_config(self, config: CNCProgrammerConfig):
        if self.external is not None:
            self.external.set_config(config)
        else:
            logging.error("External CNC runner is not defined!")

    @property
    def selected_firmware_config(self) -> FirmwareConfig | None:
        if self.external is not None:
            return self.external.selected_firmware_config
        else:
            return None
    def dps_log(self, x: int, y: int) -> DPSLog:
        if self.external is not None:
            return self.external.dps_logs[x,y]
        else:
            logging.error("External CNC runner is not defined!")

    @property
    def selected_move_axis(self) -> int:
        return self._selected_move_axis

    @selected_move_axis.setter
    def selected_move_axis(self, value: int) -> None:
        self._selected_move_axis = value


class GUIController:

    AXIS = ["X", "Y", "Z"]
    STEPS = [10, 5, 1]

    def __init__(self, view: GUIView, external: "CNCRunner"):
        self.model: GUIModel = GUIModel(external)
        self.view: GUIView = view
        self.view.root.protocol("WM_DELETE_WINDOW", self.destroy)

        # bind callbacks
        self.view.bind_browse_files_button_cb(self.evt_browse_files_clicked)
        self.view.bind_upload_button_cb(self.evt_upload_config_clicked)
        self.view.bind_start_button_cb(self.evt_start_clicked)
        self.view.bind_stop_button_cb(self.evt_stop_clicked)
        self.view.bind_move_button_cb(self.evt_move_clicked)
        for x, y in self.view.rectangles.keys():
            self.view.bind_canvas_click_cb(x, y, self.evt_show_dialog)

        for axis in range(len(GUIController.AXIS)):
            self.view.bind_move_axis_button_cb(lambda _axis=axis: self.evt_move_axis_clicked(_axis), axis)
        for step in GUIController.STEPS:
            self.view.bind_move_distance_button_cb(lambda _step=step: self.evt_move_distance_clicked(_step), step)
            self.view.bind_move_distance_button_cb(lambda _step=step: self.evt_move_distance_clicked(-_step), -step)

        # initial setup
        self.view.upload_button.config(state=DISABLED)
        self.view.start_button.config(state=DISABLED)
        self.view.stop_button.config(state=DISABLED)
        self.view.move_axis_buttons[self.model.selected_move_axis].config(style="Accent.TButton")
            #toggle visibility
        self.view.matrix_frame.grid_forget()
        self.view.error_log_frame.grid_forget()
        self.view.move_frame.grid_forget()

        # load default config
        # ???TODO: uncomment
        ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
        default_config_path: str = f"{ROOT_DIR}/../resources/config_cnc_programmer.conf"
        self.view.config_entry_text.set(default_config_path)
        self.model.config_path = default_config_path
        self.evt_upload_config_clicked()

    def destroy(self):
        print("Stoping")
        self.view.root.destroy()
        if self.model.external is not None:
            self.model.external.destroy()


    def evt_show_dialog(self, x, y) -> None:
        dps_log = self.model.dps_log(x, y)
        if not dps_log: return

        messagebox.showinfo(f"OK [{x},{y}]" if dps_log.operation_successful else f"ERROR [{x},{y}]",
                            self._format_dps_ok_msg(dps_log) if dps_log.operation_successful else self._format_dps_error_msg(dps_log))

    def evt_browse_files_clicked(self) -> None:
        # fd = filedialog.FileDialog(root)
        # file_path = fd.go(pattern="*.conf")
        ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
        file_path = filedialog.askopenfilename(initialdir=f"{ROOT_DIR}/../resources", initialfile="config_cnc_programmer.conf", filetypes=[("Config Files", "*.conf")])
        if not file_path or not len(file_path):
            # update view
            self.view.upload_message.config(text=Messages.ERROR_CONFIGURATION_SELECTION.value, foreground="red")
            return
        # update model
        self.model.config_path = file_path
        # update view
        self.view.config_entry_text.set(file_path)
        self.view.upload_button.config(state=NORMAL)

    def evt_upload_config_clicked(self) -> None:
        try:
            config = CNCProgrammerConfigParser(self.model.config_path).parse_config()
            # update view
            self._set_view_on_upload(list(config.plate_configs.values())[0])
            # propagate to CNC runner
            self.model.external_config = config
        except Exception as e:
            print(e)
            # update view
            self.view.upload_message.config(text=Messages.ERROR_CONFIGURATION_PARSING.value, foreground="red")
            return

    def evt_start_clicked(self) -> None:
        print("START clicked")
        # update view
        self._set_view_on_start()
        # update model (external)
        self.model.external_is_running = True

    def evt_stop_clicked(self) -> None:
        print("STOP clicked")
        # if self.model.external_is_running:
        # update view
        self._set_view_on_stop()
        # update model (external)
        self.model.external_is_running = False

    def evt_move_clicked(self) -> None:
        # update view
        self._set_view_on_move()

    def evt_move_axis_clicked(self, axis: int) -> None:
        #update model
        self.model.selected_move_axis = axis
        #update view
        for i in range(len(GUIController.AXIS)):
            self.view.move_axis_buttons[i].config(style="Accent.TButton" if i == axis else "TButton")

    def evt_move_distance_clicked(self, step: int) -> None:
        logging.info(f"Moving {step} mm in axis: {self.model.selected_move_axis}!")
        # call external -- BUSY wait
        self.model.external.move(Axis(self.model.selected_move_axis), step)
        # disable other buttons

        # enable other buttons

    def ex_evt_update_dps_log(self, dps_log: DPSLog) -> None:
        #TODO:
        # color: str = "green" if dps_log.operation_successful else "red"
        color: str = "green"
        self.view.rectangles[dps_log.x, dps_log.y].config(bg=color)
        if not dps_log.operation_successful:
            self.view.error_log.insert(END, self._format_dps_error_msg(dps_log))

    def ex_evt_process_completed(self) -> None:
        pass

    def ex_evt_process_interrupted(self) -> None:
        pass

    def _set_view_on_upload(self, plate_config: PlateConfig) -> None:
        self.view.upload_message.config(text=Messages.SUCCESS_CONFIGURATION_IMPORT.value, foreground="green")
        self.view.start_button.config(state=NORMAL)

        self.view.column_entry.insert(0, plate_config.columns)
        self.view.row_entry.insert(0, plate_config.rows)
        self.view.column_offset_entry.insert(0, plate_config.x_offset)
        self.view.row_offset_entry.insert(0, plate_config.y_offset)
        self.view.column_spacing_entry.insert(0, plate_config.x_spacing)
        self.view.row_spacing_entry.insert(0, plate_config.y_spacing)

    def _set_view_on_start(self):
        # toggle button state
        self.view.start_button.config(state=DISABLED)
        self.view.stop_button.config(state=NORMAL)
        self.view.move_button.config(state=DISABLED)
        # toggle frame visibility
        self.view.config_frame.grid_forget()
        self.view.plate_config_frame.grid_forget()
        self.view.move_frame.grid_forget()
        self.view.move_button.grid_forget()
        self.view.matrix_frame.grid(row=1, column=0, sticky="ns")
        # self.view.error_log_frame.grid(row=1, column=1, sticky="nsew")

    def _set_view_on_stop(self):
        # toggle button state
        self.view.start_button.config(state=NORMAL)
        self.view.stop_button.config(state=DISABLED)
        self.view.move_button.config(state=NORMAL)
        # toggle frame visibility
        self.view.config_frame.grid(row=1, column=0, padx=GUIView.PADX, pady=GUIView.PADY, sticky="nsew")
        self.view.plate_config_frame.grid(row=2, column=0, padx=GUIView.PADX, pady=GUIView.PADY, sticky="nsew")
        self.view.move_button.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        self.view.matrix_frame.grid_forget()
        self.view.error_log_frame.grid_forget()
        self.view.application_frame_content.grid_forget()



    def _set_view_on_move(self):
        # toggle button state
        self.view.start_button.config(state=NORMAL)
        self.view.stop_button.config(state=DISABLED)
        self.view.move_button.config(state=DISABLED)
        # toggle frame visibility
        self.view.plate_config_frame.grid_forget()
        self.view.matrix_frame.grid_forget()
        self.view.error_log_frame.grid_forget()
        self.view.move_frame.grid(row=3, column=0, padx=GUIView.PADX, pady=GUIView.PADY, sticky="ns")


    def _format_dps_ok_msg(self, dps_log: DPSLog) -> str:
        return (f"[programming]: fw: {self.model.external_config.firmware_default_path}, output message: {dps_log.fw_upload_message}\n" +
                f"[testing - LED current]: mode 1: {dps_log.led_current_mode1} mA, mode 2: {dps_log.led_current_mode2} mA\n" +
                f"[testing - button LED voltage]:  {dps_log.button_led_voltage}\n")

    def _format_dps_error_msg(self, dps_log: DPSLog) -> str:
        if not dps_log.fw_uploaded:
            return self._format_fw_upload_error_msg(dps_log)
        else:
            message: str = ''
            if not dps_log.led_current_mode1_passed:
                message += self._format_led_current_error_msg(dps_log, self.model.selected_firmware_config.led_current_mode1, 1)
            if not dps_log.led_current_mode2_passed:
                message += self._format_led_current_error_msg(dps_log, self.model.selected_firmware_config.led_current_mode2, 2)
            if not dps_log.button_led_voltage_passed:
                message += self._format_button_led_voltage_error_msg(dps_log, self.model.selected_firmware_config.button_led_voltage)
            return message

    def _format_fw_upload_error_msg(self, dps_log: DPSLog) -> str:
        return f"ERROR [{dps_log.x},{dps_log.y}][programming]: {dps_log.fw_upload_message}\n"
    def _format_led_current_error_msg(self, dps_log: DPSLog, spec: (int,int), mode: int=1) -> str:
        return f"ERROR [{dps_log.x},{dps_log.y}] [testing]: LED current - mode {mode} out of spec {dps_log.led_current_mode2:.0f} mA x ({spec[0]},{spec[1]}) mA\n"

    def _format_button_led_voltage_error_msg(self, dps_log: DPSLog, spec: (int,int)) -> str:
        return f"ERROR [{dps_log.x},{dps_log.y}] [testing]: Button LED voltage out of spec {dps_log.button_led_voltage:.0f} mV x ({spec[0]}, {spec[1]}) mV\n"





class GUIView(ttk.Frame):
    FG_COLOR = "#eaf205"
    PADX = (15, 15)
    PADY = (15, 15)
    DPS_HEIGHT_PX: int = 50
    DPS_WIDTH_PX: int = 100
    MIN_SIZE_PX: int = 1300

    def __init__(self, root):
        self.root = root
        self.root.maxsize(self.root.winfo_screenwidth(), root.winfo_screenheight())
        ttk.Frame.__init__(self)
        self.grid(row=0, column=0, sticky='ns')
        #self.pack(fill="both", expand=True)
        # super().__init__(root)

        self.rectangles: dict[(int, int), tk.Canvas] = {}
        self.move_axis_buttons: dict[int, ttk.Button] = {}
        self.move_distance_buttons: dict[int, ttk.Button] = {}

        self.label = ttk.Label(self, text="SCILIF CNC Programmer", justify="center", font=("-size", 20, "-weight", "bold"))
        self.label.grid(row=0, column=0, padx=GUIView.PADX, pady=GUIView.PADY, sticky="ns")

        self.config_frame = ttk.LabelFrame(self, text="Select Configuration", padding=(20, 10))
        self.config_frame.grid(row=1, column=0, padx=GUIView.PADX, pady=GUIView.PADY, sticky="nsew")
        self._create_configuration_frame_widgets()


        self.plate_config_frame = ttk.LabelFrame(self, text="Plate settings & Testing", padding=(20, 10))
        self.plate_config_frame.grid(row=2, column=0, padx=GUIView.PADX, pady=GUIView.PADY, sticky="nsew")
        self._create_plate_config_frame_widgets()


        self.application_frame = ttk.LabelFrame(self, text="Application Control", padding=(20, 10))
        self.application_frame.grid(row=3, column=0,  padx=GUIView.PADX, pady=GUIView.PADY, sticky="nsew")
        self._create_application_frame_widgets()

    def _create_configuration_frame_widgets(self) -> None:
        COLUMN_WEIGHTS = [0, 1, 0]

        self.config_label = ttk.Label(self.config_frame, text="Upload Config File:")
        self.config_label.grid(row=0, column=0, padx=GUIView.PADX, pady=GUIView.PADY, sticky="nsew")

        self.config_entry_text = tk.StringVar()
        self.config_entry = ttk.Entry(self.config_frame, textvariable=self.config_entry_text, state=DISABLED)
        self.config_entry.grid(row=0, column=1, columnspan=2, padx=GUIView.PADX, pady=GUIView.PADY, sticky="nsew")

        self.browse_files_button = ttk.Button(self.config_frame, text="Browse Files")
        self.browse_files_button.grid(row=0, column=3, padx=10, pady=10, sticky="nsew")

        self.upload_button = ttk.Button(self.config_frame, text="Upload")
        self.upload_button.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        self.upload_message = ttk.Label(self.config_frame, text="", anchor="center")
        self.upload_message.grid(row=2, columnspan=3, padx=10, pady=10, sticky="ew")

        for index, weight in enumerate(COLUMN_WEIGHTS):
            self.config_frame.columnconfigure(index, weight=weight)


    def _create_plate_config_frame_widgets(self):
        self.column_label, self.column_entry = self._generate_label_entry_pair(self.plate_config_frame, "Columns (N):", 0, 0, )
        self.row_label, self.row_entry = self._generate_label_entry_pair(self.plate_config_frame, "Rows (M):", 0, 2)

        self.column_spacing_label, self.column_spacing_entry = self._generate_label_entry_pair(self.plate_config_frame, "Spacing (X) [mm]:", 1, 0)
        self.row_spacing_label, self.row_spacing_entry = self._generate_label_entry_pair(self.plate_config_frame, "Spacing (Y) [mm]:", 1, 2)

        self.column_offset_label, self.column_offset_entry = self._generate_label_entry_pair(self.plate_config_frame, "Offset (X) of first DPS [mm]:", 2, 0)
        self.row_offset_label, self.row_offset_entry = self._generate_label_entry_pair(self.plate_config_frame, "Offset (Y) of first DPS [mm]:", 2, 2)


    def _create_application_frame_widgets(self):
        self.start_button = ttk.Button(self.application_frame, text="START")
        self.start_button.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.stop_button = ttk.Button(self.application_frame, text="STOP")
        self.stop_button.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.move_button = ttk.Button(self.application_frame, text="MOVE")
        self.move_button.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        self.application_frame.columnconfigure((0, 1), weight=1, uniform="column")

        self.application_frame_content = ttk.Frame(self.application_frame)
        self.application_frame_content.grid(row=1, column=0, columnspan=3, padx=GUIView.PADX, pady=GUIView.PADY, sticky="nsew")

        self._create_application_frame_matrix_error_log_widgets()
        self._create_application_frame_move_widgets()

    def _create_application_frame_matrix_error_log_widgets(self):

        self.matrix_frame = ttk.Frame(self.application_frame_content)
        self.matrix_frame.grid(row=0, column=0, sticky="ns")
        self.add_square_matrix_row(self.matrix_frame, 5, 10)

        self.error_log_frame = ttk.Frame(self.application_frame)
        self.error_log_frame.grid(row=0, column=1, sticky="nsew")

        self.error_log = tk.Text(self.error_log_frame, wrap="none")
        self.error_log.grid(row=0, column=0, sticky="nsew")
        self.error_log_scrollbar = ttk.Scrollbar(self.error_log_frame, orient="vertical", command=self.error_log.yview)
        self.error_log.config(yscrollcommand=self.error_log_scrollbar.set)

        scroll_text = lambda event: self.error_log.yview_scroll(-1 * (event.delta // 120), "units")
        self.error_log.bind("<MouseWheel>", scroll_text)

    def _create_application_frame_move_widgets(self):

        self.move_frame = ttk.Frame(self.application_frame_content)
        self.move_frame.grid(row=0, column=0, padx=GUIView.PADX, pady=GUIView.PADY, sticky="ns")

        for i, axis in enumerate(GUIController.AXIS):
            button = ttk.Button(self.move_frame, text=axis)
            button.grid(row=0, column=i, padx=GUIView.PADX, pady=GUIView.PADY,  sticky="nsew")
            self.move_axis_buttons[i] = button

        for i, step in enumerate(GUIController.STEPS):
            button = ttk.Button(self.move_frame, text=f"+{step} mm")
            button.grid(row=1, column=i*2, padx=GUIView.PADX, pady=GUIView.PADY,  sticky="nsew")
            self.move_distance_buttons[step] = button
            button = ttk.Button(self.move_frame, text=f"-{step} mm")
            button.grid(row=1, column=i*2 +1, padx=GUIView.PADX, pady=GUIView.PADY,  sticky="nsew")
            self.move_distance_buttons[-step] = button



    def add_square_matrix_row(self, matrix_frame: ttk.Frame, columns: int, rows: int):
        for row in range(rows):
            for column in range(columns):
                canvas = tk.Canvas(matrix_frame, width=GUIView.DPS_WIDTH_PX, height=GUIView.DPS_HEIGHT_PX, bg="grey")
                canvas.grid(row=row, column=column, sticky="nsew")
                self.rectangles[(column, rows - (row+1))] = canvas

    def set_controller(self, controller: GUIController):
        self.controller = controller

    def _generate_label_entry_pair(self, frame, label_text, row, column, state=NORMAL) -> (ttk.Label, ttk.Entry):
        label = ttk.Label(frame, text=label_text)
        label.grid(row=row, column=column, padx=GUIView.PADX, pady=GUIView.PADY)
        entry = ttk.Entry(frame, state=state)
        entry.grid(row=row, column=column + 1, padx=GUIView.PADX, pady=GUIView.PADY)
        return (label, entry)

    # def bind_config_entry_focus_in_cb(self, callback):
    #     self.config_entry.bind("<FocusIn>", callback)

    def bind_upload_button_cb(self, callback):
        self.upload_button.config(command=callback)

    def bind_browse_files_button_cb(self, callback):
        self.browse_files_button.config(command=callback)

    def bind_start_button_cb(self, callback):
        self.start_button.config(command=callback)

    def bind_stop_button_cb(self, callback):
        self.stop_button.config(command=callback)

    def bind_canvas_click_cb(self, x: int, y: int, callback: Callable[[int, int], None]):
        self.rectangles[(x, y)].bind("<Button-1>", lambda evt, _x=x, _y=y: callback(_x, _y))

    def bind_move_button_cb(self, callback):
        self.move_button.config(command=callback)

    def bind_move_axis_button_cb(self, callback, axis: int):

        self.move_axis_buttons[axis].config(command=callback)

    def bind_move_distance_button_cb(self, callback, distance: int):
        self.move_distance_buttons[distance].config(command=callback)


    # def update_info_log(self, text):
    #     self.info_log_text.insert(tk.END, text)

    # def update_malfunction_log(self, text):
    #     self.malfunction_log_text.insert(tk.END, text)


def create_root_window() -> tk.Tk:

    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

    root = tk.Tk()
    root.title('SCILIF CNC PROGRAMMER')
    root.tk.call("source", f"{ROOT_DIR}/../../../lib/theme/azure.tcl")
    root.tk.call("set_theme", "dark")

    # Set a minsize for the window, and place it in the middle
    root.update()
    root.grid_columnconfigure(0, minsize=GUIView.MIN_SIZE_PX, weight=1)
    root.minsize(root.winfo_width(), root.winfo_height())
    root.maxsize(root.winfo_screenwidth(), root.winfo_screenheight())
    x_coordinate = int((root.winfo_screenwidth() / 2) - (root.winfo_width() / 2))
    y_coordinate = int((root.winfo_screenheight() / 2) - (root.winfo_height() / 2))
    # root.geometry(f"+{x_coordinate}+{y_coordinate - 20}")

    w, h = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry("%dx%d+0+0" % (w, h-20))
    root.bind_all('<Control-c>', lambda _: root.destroy())
    return root



if __name__ == "__main__":

    logging.getLogger().setLevel(logging.INFO)

    root: tk.Tk = create_root_window()
    view = GUIView(root)
    controller = GUIController(view, None)
    view.set_controller(controller)

    root.mainloop()
