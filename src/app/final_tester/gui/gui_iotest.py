from __future__ import annotations

import logging
import os
import tkinter as tk
from enum import Enum
from tkinter import BOTH, BOTTOM, DISABLED, LEFT, NORMAL, RIGHT, TOP, X, Y, YES, ttk, messagebox, END
from app.final_tester.rpi_board import RPiBoard



class Pins(Enum):
    BINDER = 0
    AXIS_1 = 1
    AXIS_2 = 2
    START = 3


class GUIView(ttk.Frame):
    PADX = (15, 15)
    PADY = (15, 15)



    def __init__(self, root, board: RPiBoard):
        self.root = root
        self.root.maxsize(self.root.winfo_screenwidth(), root.winfo_screenheight())
        ttk.Frame.__init__(self)
        self.board = board

        self.output_buttons: dict[Pins, (ttk.Button, ttk.Button)] = {}
        self.input_labels: dict[Pins, ttk.Label] = {}

        self.grid(row=0, column=0, sticky='ns')

        self.output_frame = ttk.LabelFrame(self, text="Výstupy")
        self.output_frame.grid(row=0, column=0, padx=GUIView.PADX, pady=GUIView.PADY)

        label = ttk.Label(self.output_frame, text="Odjistit/Zajistit")
        label.grid(row=0, column=0, padx=GUIView.PADX, pady=GUIView.PADY)
        high_button = ttk.Button(self.output_frame, text="High", command=lambda: self.write_pin(Pins.BINDER, True))
        high_button.grid(row=0, column=1, padx=GUIView.PADX, pady=GUIView.PADY)
        low_button = ttk.Button(self.output_frame, text="Low", command=lambda: self.write_pin(Pins.BINDER, False))
        low_button.grid(row=0, column=2, padx=GUIView.PADX, pady=GUIView.PADY)
        self.output_buttons[Pins.BINDER] = (high_button, low_button)


        label = ttk.Label(self.output_frame, text="Vysunout/Zasunout")
        label.grid(row=1, column=0, padx=GUIView.PADX, pady=GUIView.PADY)
        high_button = ttk.Button(self.output_frame, text="High", command=lambda: self.write_pin(Pins.AXIS_1, True))
        high_button.grid(row=1, column=1, padx=GUIView.PADX, pady=GUIView.PADY)
        low_button = ttk.Button(self.output_frame, text="Low", command=lambda: self.write_pin(Pins.AXIS_1, False))
        low_button.grid(row=1, column=2, padx=GUIView.PADX, pady=GUIView.PADY)
        self.output_buttons[Pins.AXIS_1] = (high_button, low_button)


        label = ttk.Label(self.output_frame, text="Stisknout/Uvolnit")
        label.grid(row=2, column=0, padx=GUIView.PADX, pady=GUIView.PADY)
        high_button = ttk.Button(self.output_frame, text="High", command=lambda: self.write_pin(Pins.AXIS_2, True))
        high_button.grid(row=2, column=1, padx=GUIView.PADX, pady=GUIView.PADY)
        low_button = ttk.Button(self.output_frame, text="Low", command=lambda: self.write_pin(Pins.AXIS_2, False))
        low_button.grid(row=2, column=2, padx=GUIView.PADX, pady=GUIView.PADY)
        self.output_buttons[Pins.AXIS_2] = (high_button, low_button)



        self.input_frame = ttk.LabelFrame(self, text="Vstupy")
        self.input_frame.grid(row=0, column=1, padx=GUIView.PADX, pady=GUIView.PADY)

        label = ttk.Label(self.input_frame, text="Odjistit/Zajistit")
        label.grid(row=0, column=0, padx=GUIView.PADX, pady=GUIView.PADY)
        label = ttk.Label(self.input_frame, text="???")
        label.grid(row=0, column=1, padx=GUIView.PADX, pady=GUIView.PADY)
        self.input_labels[Pins.BINDER] = label

        label = ttk.Label(self.input_frame, text="Vysunout/Zasunout")
        label.grid(row=1, column=0, padx=GUIView.PADX, pady=GUIView.PADY)
        label = ttk.Label(self.input_frame, text="???")
        label.grid(row=1, column=1, padx=GUIView.PADX, pady=GUIView.PADY)
        self.input_labels[Pins.AXIS_1] = label

        label = ttk.Label(self.input_frame, text="Stisknout/Uvolnit")
        label.grid(row=2, column=0, padx=GUIView.PADX, pady=GUIView.PADY)
        label = ttk.Label(self.input_frame, text="???")
        label.grid(row=2, column=1, padx=GUIView.PADX, pady=GUIView.PADY)
        self.input_labels[Pins.AXIS_2] = label

        label = ttk.Label(self.input_frame, text="START")
        label.grid(row=3, column=0, padx=GUIView.PADX, pady=GUIView.PADY)
        label = ttk.Label(self.input_frame, text="???")
        label.grid(row=3, column=1, padx=GUIView.PADX, pady=GUIView.PADY)
        self.input_labels[Pins.START] = label

        # Schedule the next update
        self.read_pins()

    def write_pin(self, pin: Pins, value: bool) -> None:
        self.output_buttons[pin][int(not value)].config(style="Accent.TButton")
        self.output_buttons[pin][value].config(style="TButton")

        if pin == Pins.BINDER:
            self.board.write_pin(self.board.binder_out_pin, value)
        elif pin == Pins.AXIS_1:
            self.board.write_pin(self.board.axis_1_movement_out_pin, value)
        elif pin == Pins.AXIS_2:
            self.board.write_pin(self.board.axis_2_movement_out_pin, value)

    def read_pins(self):
        print("Reading pins...")
        high_low = lambda value: "High" if value is True else "Low"
        self.input_labels[Pins.BINDER].config(text=high_low(self.board.binder_in_pin.value))
        self.input_labels[Pins.AXIS_1].config(text=high_low(self.board.axis_1_movement_in_pin.value))
        self.input_labels[Pins.AXIS_2].config(text=high_low(self.board.axis_2_movement_in_pin.value))
        self.input_labels[Pins.START].config(text=high_low(self.board.start_in_pin.value))

        self.root.after(1000, self.read_pins)  # Call update_ui() after 1000 milliseconds (1 second)



def create_root_window() -> tk.Tk:

    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    root = tk.Tk()
    root.title('SCILIF CNC PROGRAMMER')
    root.tk.call("source", f"{ROOT_DIR}/../../../lib/theme/azure.tcl")
    root.tk.call("set_theme", "dark")

    # Set a minsize for the window, and place it in the middle
    root.update()
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
    board = RPiBoard()
    root: tk.Tk = create_root_window()
    view = GUIView(root, board)
    root.mainloop()