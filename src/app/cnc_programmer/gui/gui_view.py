from __future__ import annotations

import logging
import os
import tkinter as tk
from enum import Enum
from tkinter import ttk
from typing import Callable, List

from PIL import Image, ImageTk

from app.cnc_programmer.gui.gui_utils import _generate_label_entry_pair, set_column_weights
from app.cnc_programmer.gui.scrollable_frame import EmbeddedScrollableFrame, CustomFullScreenFrame

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

SMALL_PADX = (5, 5)
SMALL_PADY = (5, 5)
PADX = (10, 10)
PADY = (10, 10)

BIG_FONT = 16
MEDIUM_FONT = 11


class Messages(Enum):
    ERROR_CONFIGURATION_SELECTION = "Žádná konfigurace nebyla vybrána!"
    ERROR_CONFIGURATION_PARSING = "Chyba v konfiguraci!"
    SUCCESS_CONFIGURATION_IMPORT = "Konfigurace byla úspěšně nahrána!"

class MenuFrames(Enum):
    SETTINGS = "Nastavení"
    MANUAL_MODE = "Manuální mód"
    AUTOMATIC_CYCLE = "Automatický cyklus"
    SCROLL_TEST = "Manuál"

class ScrollableTestFrame(ttk.Frame):

    def __init__(self, parent_frame: ttk.Frame) -> None:
        super().__init__(parent_frame)
        self.grid_columnconfigure(0, weight=1)

        for i in range(100):
            label = ttk.Label(self, text=f"Label {i}")
            label.grid(row=i, column=0)


class SettingsFrame(ttk.Frame):

    def __init__(self, parent_frame: ttk.Frame, parent_view: GUIView) -> None:
        super().__init__(parent_frame)
        self.view = parent_view
        self.grid_columnconfigure(0, weight=1)

        frame = ttk.LabelFrame(self, text="Výběr Konfigurace")
        frame.grid(row=0, column=0, padx=PADX, pady=PADY, sticky="nsew")
        self._create_configuration_frame_widgets(frame)

        frame = ttk.LabelFrame(self, text="Nastavení Desky")
        frame.grid(row=1, column=0, padx=PADX, pady=PADY, sticky="nsew")
        self._create_plate_config_frame_widgets(frame)

        frame = ttk.LabelFrame(self, text="Nastavení Firmware")
        frame.grid(row=2, column=0, padx=PADX, pady=PADY, sticky="nsew")
        self._create_firmware_config_frame_widgets(frame)

    def _create_configuration_frame_widgets(self, frame: ttk.LabelFrame) -> None:
        COLUMN_WEIGHTS = [0, 1, 0]

        label = ttk.Label(frame, text="Konfigurační soubor:")
        label.grid(row=0, column=0, padx=PADX, pady=PADY, sticky="nsew")

        entry = ttk.Entry(frame)
        entry.grid(row=0, column=1, columnspan=2, padx=PADX, pady=PADY, sticky="nsew")
        self.view.config_entry = entry

        button = ttk.Button(frame, text="Procházet")
        button.grid(row=0, column=3, padx=10, pady=10, sticky="nsew")
        self.view.browse_files_button = button

        button = ttk.Button(frame, text="Nahrát")
        button.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        self.view.upload_button = button

        label = ttk.Label(frame, text="", anchor="center")
        label.grid(row=2, columnspan=3, padx=10, pady=10, sticky="ew")
        self.view.upload_message = label

        set_column_weights(frame, COLUMN_WEIGHTS)


    def _create_plate_config_frame_widgets(self, frame: ttk.LabelFrame):
        COLUMN_WEIGHTS = [2, 1, 2, 1]

        _, self.view.column_entry = _generate_label_entry_pair(frame, "Sloupce (N):", 0, 0, PADX, PADY)
        _, self.view.row_entry = _generate_label_entry_pair(frame, "Řádky (M):", 0, 2, PADX, PADY)

        _, self.view.column_spacing_entry = _generate_label_entry_pair(frame, "Rozteč (X) [mm]:", 1, 0, PADX, PADY)
        _, self.view.row_spacing_entry = _generate_label_entry_pair(frame, "Rozteč (Y) [mm]:", 1, 2, PADX, PADY)

        # self.column_offset_label, self.column_offset_entry = self._generate_label_entry_pair(self.plate_config_frame, "Offset (X) of first DPS [mm]:", 2, 0, GUIView.PADX, GUIView.SMALL_PADY)
        # self.row_offset_label, self.row_offset_entry = self._generate_label_entry_pair(self.plate_config_frame, "Offset (Y) of first DPS [mm]:", 2, 2, GUIView.PADX, GUIView.SMALL_PADY)

        set_column_weights(frame, COLUMN_WEIGHTS)

    def _create_firmware_config_frame_widgets(self, frame: ttk.LabelFrame):
        COLUMN_WEIGHTS = [2, 1, 2, 1]

        _, self.view.fw_path_entry = _generate_label_entry_pair(frame, "Firmware:", 0, 0, PADX, PADY)
        _, self.view.fw_type_entry = _generate_label_entry_pair(frame, "Typ firmware:", 0, 2, PADX, PADY)

        _, self.view.fw_led_current_entry = _generate_label_entry_pair(frame, "Přípustný proud LED [mA]:", 1, 0, PADX, PADY)
        _, self.view.fw_button_led_voltage_entry = _generate_label_entry_pair(frame, "Přípustné napětí LED tlačítka [mV]:", 1, 2, PADX, PADY)
        _, self.view.fw_r_feedback_voltage_entry = _generate_label_entry_pair(frame, "Přípustné napětí ZV rezistoru [mV]:", 2, 0, PADX, PADY)
        _, self.view.fw_button_change_duration_entry = _generate_label_entry_pair(frame, "Změna módu [ms]:", 2, 2, PADX, PADY)
        self.view.fw_led_current_mode2_label, self.view.fw_led_current_mode2_entry = _generate_label_entry_pair(frame, "Přípustný proud LED (slabý mód) [mA]:", 3, 0, PADX, PADY)

        set_column_weights(frame, COLUMN_WEIGHTS)


class ManualModeFrame(ttk.Frame):

    def __init__(self, parent_frame: ttk.Frame, parent_view: GUIView) -> None:
        super().__init__(parent_frame)
        self.view = parent_view
        self.grid_columnconfigure(0, weight=1)

        frame = ttk.LabelFrame(self, text="Kontrolní panel")
        frame.grid(row=0, column=0, sticky="nsew", padx=PADX, pady=PADY)
        set_column_weights(frame, [1, 1, 1, 2])
        button = ttk.Button(frame, text="Nastavit Základnu")
        button.grid(row=0, column=0, padx=PADX, pady=PADY, sticky="nsew")
        self.view.set_home_button = button
        button = ttk.Button(frame, text="Do Základny")
        button.grid(row=0, column=1, padx=PADX, pady=PADY, sticky="nsew")
        self.view.go_home_button = button
        button = ttk.Button(frame, text="Stop")
        button.grid(row=0, column=2, padx=PADX, pady=PADY, sticky="nsew")
        self.view.manual_stop_button = button
        label = ttk.Label(frame, text="Současná pozice [mm]: ?", font=("-size", MEDIUM_FONT, "-weight", "bold"))
        label.grid(row=0, column=3, padx=PADX, pady=PADY, sticky="e")
        self.view.manual_current_pos_label_mm = label


        manual_mode_frame = ttk.LabelFrame(self, text="Výběr Osy a Vzdálenosti")
        manual_mode_frame.grid(row=1, column=0, sticky="nsew", padx=PADX, pady=PADY)
        manual_mode_frame.columnconfigure(0, weight=1)

        axis_frame = ttk.Frame(manual_mode_frame)
        axis_frame.grid(row=0, column=0, sticky="nsew")
        step_frame = ttk.Frame(manual_mode_frame)
        step_frame.grid(row=1, column=0, sticky="nsew")

        self._create_axis_widgets(axis_frame)
        self._create_step_widgets(step_frame)

    def _create_axis_widgets(self, frame: ttk.Frame):

        COLUMN_WEIGHTS = [1, 1, 1]

        for i, axis in enumerate(GUIView.AXIS):
            button = ttk.Button(frame, text=axis)
            button.grid(row=0, column=i, padx=PADX, pady=PADY, sticky="nsew")
            self.view.move_axis_buttons[i] = button

        set_column_weights(frame, COLUMN_WEIGHTS)


    def _create_step_widgets(self, frame: ttk.Frame):

        COLUMN_WEIGHTS = [1, 1, 1, 1, 1]

        for i, step in enumerate(GUIView.STEPS):
            button = ttk.Button(frame, text=f"+{step} mm")
            button.grid(row=0, column=i, padx=PADX, pady=PADY, sticky="nsew")
            self.view.move_distance_buttons[step] = button

            button = ttk.Button(frame, text=f"-{step} mm")
            button.grid(row=1, column=i, padx=PADX, pady=PADY, sticky="nsew")
            self.view.move_distance_buttons[-step] = button

        set_column_weights(frame, COLUMN_WEIGHTS)



class AutomaticCycleFrame(ttk.Frame):

    DPS_HEIGHT_PX: int = 47
    DPS_WIDTH_PX: int = 88

    def __init__(self, parent_frame: ttk.Frame, parent_view: GUIView) -> None:
        super().__init__(parent_frame)
        self.grid_columnconfigure(0, weight=1)
        self.view = parent_view

        frame = ttk.Frame(self)
        frame.grid(row=0, column=0, padx=PADX, pady=(0, 0), sticky="nsew")
        label = ttk.Label(frame, text="Cílová pozice: ?", font=("-size", MEDIUM_FONT, "-weight", "bold"))
        label.pack(side=tk.LEFT, padx=(100, 100), pady=(0, 5))
        self.view.current_pos_label = label
        label = ttk.Label(frame, text="Současná pozice [mm]: ?", font=("-size", MEDIUM_FONT, "-weight", "bold"))
        label.pack(side=tk.RIGHT, padx=(100, 100), pady=(0, 5))
        self.view.current_pos_label_mm = label

        application_frame = ttk.LabelFrame(self, text="Kontrolní Panel")
        application_frame.grid(row=1, column=0, padx=PADX, pady=(0, 5), sticky="nsew")
        application_frame.columnconfigure(0, weight=1)
        self._create_application_frame_widgets(application_frame)

    def _create_application_frame_widgets(self, parent_frame: ttk.LabelFrame):

        # Row with buttons
        frame = ttk.Frame(parent_frame)
        frame.grid(row=0, column=0, padx=SMALL_PADX, pady=(0, 0), sticky="nsew")
        set_column_weights(frame, [1, 1, 1, 1])

        button = ttk.Button(frame, text="Start")
        button.grid(row=0, column=0, padx=PADX, pady=SMALL_PADY, sticky="nsew")
        self.view.start_button = button
        button = ttk.Button(frame, text="Stop")
        button.grid(row=0, column=1, padx=PADX, pady=SMALL_PADY, sticky="nsew")
        self.view.pause_button = button
        button = ttk.Button(frame, text="Pokračovat")
        button.grid(row=0, column=2, padx=PADX, pady=SMALL_PADY, sticky="nsew")
        self.view.resume_button = button
        button = ttk.Button(frame, text="Ukončit")
        button.grid(row=0, column=3, padx=PADX, pady=SMALL_PADY, sticky="nsew")
        self.view.finish_button = button

        # Row with positions
        frame = ttk.Frame(parent_frame)
        frame.grid(row=1, column=0, padx=PADX, pady=(0, 0), sticky="nsew")

        label = ttk.Label(frame, text="Z pozice X:")
        label.pack(side=tk.LEFT, padx=PADX, pady=SMALL_PADY)
        entry = ttk.Entry(frame, width=10)
        entry.pack(side=tk.LEFT, padx=PADX, pady=SMALL_PADY)
        self.view.start_from_x_entry = entry
        label = ttk.Label(frame, text="Z pozice Y:")
        label.pack(side=tk.LEFT, padx=PADX, pady=SMALL_PADY)
        entry = ttk.Entry(frame, width=10)
        entry.pack(side=tk.LEFT, padx=PADX, pady=SMALL_PADY)
        self.view.start_from_y_entry = entry


        # Row with text box and metrices
        frame = ttk.Frame(parent_frame)
        frame.grid(row=2, column=0, padx=PADX, pady=PADY, sticky="nsew")

        self.matrix_frame = ttk.Frame(frame)
        self.matrix_frame.pack(side=tk.LEFT, fill=tk.Y, padx=SMALL_PADX, pady=(0, 0))

        frame = ttk.Frame(frame)
        frame.pack(side=tk.RIGHT, fill=tk.Y, expand=1, padx=(0, 0), pady=(0, 0))
        # label = ttk.Label(frame, text="Výpis chyb cyklu:", font=("-size", MEDIUM_FONT, "-weight", "bold"))
        # label.pack(side=tk.TOP, anchor=tk.W, padx=(0, 0), pady=SMALL_PADY)
        error_log = tk.Text(frame, wrap='none')
        error_log_scrollbar_y = ttk.Scrollbar(frame, orient="vertical", command=error_log.yview)
        error_log.config(yscrollcommand=error_log_scrollbar_y.set)
        error_log_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        error_log_scrollbar_x = ttk.Scrollbar(frame, orient="horizontal", command=error_log.xview)
        error_log.config(xscrollcommand=error_log_scrollbar_x.set)
        error_log_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        error_log.pack(fill=tk.BOTH, expand=1)
        self.view.error_log = error_log

    def plot_square_matrices(self, columns: int, rows: int, colour: str = "grey") -> None:
        for canvas in self.view.cycle_rectangles.values():
            canvas.grid_forget()
            canvas.delete("all")
        for label in self.view.cycle_labels:
            label.destroy()

        for row in range(rows):
            # add vertical  labels
            label = ttk.Label(self.matrix_frame, text=str(rows - (row+1)))
            label.grid(row=row, column=0, sticky="nsew", padx=(5, 5), pady=(5, 5))
            self.view.cycle_labels.append(label)

            # add matrices
            for column in range(columns):
                canvas = tk.Canvas(self.matrix_frame, width=AutomaticCycleFrame.DPS_WIDTH_PX, height=AutomaticCycleFrame.DPS_HEIGHT_PX, bg=colour)
                canvas.grid(row=row, column=column+1, sticky="nsew", padx=(2, 2), pady=(2, 2))
                self.view.cycle_rectangles[(column, rows - (row + 1))] = canvas
        # add horizontal labels
        for column in range(columns):
            label = ttk.Label(self.matrix_frame, text=str(column), anchor="center")
            label.grid(row=rows, column=column+1, sticky="nsew", padx=(5, 5), pady=(5, 5))
            self.view.cycle_labels.append(label)

    def reset_color_of_matrices(self, colour: str) -> None:
        for canvas in self.view.cycle_rectangles.values():
            canvas.config(bg=colour)

    def reset_white_matrices(self, colour: str) -> None:
        for canvas in self.view.cycle_rectangles.values():
            if canvas["background"] == "white":
                canvas.config(bg=colour)


class GUIView(CustomFullScreenFrame):

    PADX_FRAME = (20, 20)
    PADY_FRAME = (12.5, 12.5)
    MENU_IMAGE_SIZE_PX = 48

    CURRENT_POS_TEXT = "Cílová pozice [x,y]: {value}"
    CURRENT_POS_TEXT_MM = "Současná pozice [x,y,z] [mm]: {value}"

    AXIS = ["X", "Y", "Z"]
    STEPS = [40, 20, 10, 5, 1]

    def __init__(self, root: tk.Tk):
        super().__init__(root)

        # Settings frame
        self.config_entry: tk.Entry = None
        self.browse_files_button: ttk.Button = None
        self.upload_message: ttk.Label = None
        self.upload_button: ttk.Button = None
        self.column_entry: ttk.Entry = None
        self.row_entry: ttk.Entry = None
        self.column_spacing_entry: ttk.Entry = None
        self.row_spacing_entry: ttk.Entry = None
        self.fw_path_entry: ttk.Entry = None
        self.fw_type_entry: ttk.Entry = None
        self.fw_led_current_entry: ttk.Entry = None
        self.fw_led_current_mode2_label: ttk.Label= None
        self.fw_led_current_mode2_entry: ttk.Entry = None
        self.fw_button_led_voltage_entry: ttk.Entry = None
        self.fw_r_feedback_voltage_entry: ttk.Entry = None
        self.fw_button_change_duration_entry: ttk.Entry = None

        # Manual mode frame
        self.move_axis_buttons: dict[int, ttk.Button] = {}
        self.move_distance_buttons: dict[int, ttk.Button] = {}
        self.manual_stop_button: ttk.Button = None
        self.go_home_button: ttk.Button = None
        self.set_home_button: ttk.Button = None
        self.manual_current_pos_label_mm: ttk.Label = None

        # Automatic cycle frame
        self.current_pos_label: ttk.Label = None
        self.current_pos_label_mm: ttk.Label = None
        self.cycle_rectangles: dict[(int, int), tk.Canvas] = {}
        self.cycle_labels: List[ttk.Label] = []
        self.error_log: tk.Text = None
        self.start_button: ttk.Button = None
        self.pause_button: ttk.Button = None
        self.resume_button: ttk.Button = None
        self.finish_button: ttk.Button = None
        self.start_from_x_entry: ttk.Entry = None
        self.start_from_y_entry: ttk.Entry = None

        # Generate Left menu
        self.menu_frame = ttk.Frame(self)
        self.menu_frame.pack(side=tk.LEFT, fill=tk.Y, pady=GUIView.PADY_FRAME)
        self._populate_menu_frame()

        # Generate top header
        label = ttk.Label(self, text="SCILIF CNC Programátor", font=("-size", BIG_FONT, "-weight", "bold"))
        label.pack(side=tk.TOP, pady=GUIView.PADY_FRAME)
        # self.state_label = ttk.Label(self, text="?", )
        # self.state_label.pack(side=tk.TOP, pady=GUIView.PADY_FRAME)

        # Generate the scrollable content
        self.scrollable_frame = EmbeddedScrollableFrame(self)
        self.scrollable_frame.pack(fill=tk.BOTH, expand=1)
        self.content_frame = self.scrollable_frame.scrollable_frame
        # self.content_frame.pack(fill=tk.BOTH, expand=1)


        # preselect first item
        first_item = self.menu_tree.get_children()[0]
        self.menu_tree.selection_set(first_item)
        self.menu_tree.focus(first_item)

        self._generate_frames()

    def set_controller(self, controller: "GUIController"):
        self.controller = controller

    def bind_canvas_click_cb(self, x: int, y: int, callback: Callable[[int, int], None]):
        self.cycle_rectangles[(x, y)].bind("<Button-1>", lambda evt, _x=x, _y=y: callback(_x, _y))

    def on_menu_select(self, event) -> None:
        selected_item: str = event.widget.selection()[0]
        selected_menu_frame: MenuFrames = MenuFrames(self.menu_tree.item(selected_item, "text"))
        # Add your code to handle menu item selection here
        logging.debug(f"[GUI]: selected - {selected_menu_frame.value}")

        # first_item = self.menu_tree.get_children()[0]
        # self.menu_tree.selection_set(first_item)
        # self.menu_tree.focus(first_item)
        # return

        for frame in self.frames.values():
            if frame is not None:
                frame.pack_forget()
        if selected_menu_frame in self.frames.keys() and self.frames[selected_menu_frame] is not None:
            self.frames[selected_menu_frame].pack(side=tk.BOTTOM, fill=tk.BOTH, expand=1, padx=GUIView.PADX_FRAME, pady=GUIView.PADY_FRAME)
            self.scrollable_frame.canvas.xview_moveto(0)
            self.scrollable_frame.canvas.yview_moveto(0)

    def _populate_menu_frame(self) -> None:

        s = ttk.Style()
        s.configure('Treeview', rowheight=GUIView.MENU_IMAGE_SIZE_PX + 10)

        # Create a Treeview widget as the menu bar
        menu_tree = ttk.Treeview(self.menu_frame, selectmode="browse")
        menu_tree.pack(side=tk.LEFT, fill=tk.Y, padx=SMALL_PADX, pady=SMALL_PADY)
        menu_tree.heading("#0", text="Menu", anchor="center")

        self.menu_tree = menu_tree

        # Define menu items and icons
        menu_items = [
            {"text": MenuFrames.SETTINGS.value, "icon": "settings.png"},
            {"text": MenuFrames.MANUAL_MODE.value, "icon": "manual.png"},
            {"text": MenuFrames.AUTOMATIC_CYCLE.value, "icon": "cycle.png"},
            {"text": MenuFrames.SCROLL_TEST.value, "icon": "home.png"},
        ]
        self.images = []

        # Insert menu items with icons
        for item in menu_items:
            image = Image.open(f"{ROOT_DIR}/icons/{item['icon']}")
            image = image.resize((GUIView.MENU_IMAGE_SIZE_PX, GUIView.MENU_IMAGE_SIZE_PX), Image.LANCZOS)

            image_tk = ImageTk.PhotoImage(image)
            menu_tree.insert("", "end", text=item["text"], image=image_tk)
            menu_tree.bind("<<TreeviewSelect>>", self.on_menu_select)

            # to prevent the image from being garbage collected
            self.images.append(image_tk)


    def _generate_frames(self) -> None:
        self.settings_frame = SettingsFrame(self.content_frame, self)
        self.manual_mode_frame = ManualModeFrame(self.content_frame, self)
        self.automatic_cycle_frame = AutomaticCycleFrame(self.content_frame, self)

        self.f = ScrollableTestFrame(self.content_frame)
        self.frames = {
            MenuFrames.SETTINGS: self.settings_frame,
            MenuFrames.MANUAL_MODE: self.manual_mode_frame,
            MenuFrames.AUTOMATIC_CYCLE: self.automatic_cycle_frame,
            MenuFrames.SCROLL_TEST: self.f
        }


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
    view = GUIView(root)
    view.pack(fill=tk.BOTH, expand=1)

    root.update()
    root.mainloop()

