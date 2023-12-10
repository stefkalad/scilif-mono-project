from __future__ import annotations

import logging
import os
import random
import tkinter as tk
from enum import Enum
from tkinter import ttk


# from PIL import Image, ImageTk



class Pins(Enum):
    BINDER = 0
    AXIS_1 = 1
    AXIS_2 = 2
    START = 3

class GUIController:

    def __init__(self, view: GUIView, external: "FinalTester"):
        self.view = view
        self.external = external

        self.view.root.protocol("WM_DELETE_WINDOW", self.destroy)
        # self.ex_evt_show_image()

    def destroy(self):
        logging.info("Stopping...")
        self.view.root.evt_destroy()
        if self.external is not None:
            self.external.stop()

    def ex_evt_change_input_pin(self, pin: Pins, value) -> None:
        self.view.input_labels[pin].config(text="High" if value is True else "Low")

    def ex_evt_change_output_pin(self, pin: Pins, value) -> None:
        self.view.output_labels[pin].config(text="High" if value is True else "Low")

    def ex_evt_show_image(self, image) -> None:
        pass

    def ex_evt_show_measurement_output(self, barcode: str = "10123115824", usb_current= 315.1, l_pd_current= 305.1, r_pd_current= 305.1, button_led=True) -> None:
        random_number = lambda: random.randint(20, 40) / 10.0
        usb_current += random_number()
        l_pd_current += random_number()
        r_pd_current += random_number()
        self.view.qr_code_label.config(text=barcode, foreground="green", )
        self.view.measured_USB_current_label.config(text=f"{usb_current:.1f}")
        self.view.measured_L_LED_current_label.config(text=f"{l_pd_current:.1f}")
        self.view.measured_R_LED_current_label.config(text=f"{r_pd_current:.1f}")
        self.view.button_led_label.config(text="OK", foreground="green")

    def ex_evt_clear_measurement_output(self) -> None:
        self.view.qr_code_label.config(text="???", foreground="white")
        self.view.measured_USB_current_label.config(text="???")
        self.view.measured_L_LED_current_label.config(text="???")
        self.view.measured_R_LED_current_label.config(text="???")
        self.view.button_led_label.config(text="???", foreground="white")

    def ex_evt_show_dialog(self):
        self.view.create_custom_message_box()

    # def ex_evt_show_image(self) -> None:
    #     ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    #     image = Image.open(f"{ROOT_DIR}/camera_ok.jpeg")  # Replace with your image file path
    #     self.tk_image = ImageTk.PhotoImage(image)
    #     self.view.image_label.config(image=self.tk_image)




class GUIView(ttk.Frame):
    PADX = (15, 15)
    PADY = (15, 15)

    def __init__(self, root):
        self.root = root
        self.root.maxsize(self.root.winfo_screenwidth(), root.winfo_screenheight())
        ttk.Frame.__init__(self)
        self.grid(row=0, column=0, sticky='ns')

        self.output_labels: dict[Pins, ttk.Label] = {}
        self.input_labels: dict[Pins, ttk.Label] = {}
        self.qr_code_label: ttk.Label
        self.button_led_label: ttk.Label
        self.measured_USB_current_label: ttk.Label
        self.measured_L_LED_current_label: ttk.Label
        self.measured_R_LED_current_label: ttk.Label
        self.image_label: ttk.Label
        self.message_box = None


        self.label = ttk.Label(self, text="SCILIF Final Tester", justify="center", font=("-size", 16, "-weight", "bold"))
        self.label.grid(row=0, column=0, padx=GUIView.PADX, pady=GUIView.PADY, sticky="ns")

        self.device_frame = ttk.LabelFrame(self, text="Naměřené hodnoty")
        self.device_frame.grid(row=1, column=0, columnspan=2, padx=GUIView.PADX, pady=GUIView.PADY, sticky="nsew")

        label = ttk.Label(self.device_frame, text="QR Code")
        label.grid(row=0, column=0, columnspan=2, padx=GUIView.PADX, pady=GUIView.PADY, sticky="nsew")
        label = ttk.Label(self.device_frame, text="???")
        label.grid(row=0, column=1, columnspan=2, padx=GUIView.PADX, pady=GUIView.PADY, sticky="nsew")
        self.qr_code_label = label

        label = ttk.Label(self.device_frame, text="LED v tlačítku")
        label.grid(row=1, column=0, padx=GUIView.PADX, pady=GUIView.PADY, sticky="nsew")
        label = ttk.Label(self.device_frame, text="???")
        label.grid(row=1, column=1, padx=GUIView.PADX, pady=GUIView.PADY, sticky="nsew")
        self.button_led_label = label

        label = ttk.Label(self.device_frame, text="Proud USB [mA]")
        label.grid(row=1, column=2, padx=GUIView.PADX, pady=GUIView.PADY, sticky="nsew")
        label = ttk.Label(self.device_frame, text="???")
        label.grid(row=1, column=3, padx=GUIView.PADX, pady=GUIView.PADY, sticky="nsew")
        self.measured_USB_current_label = label

        label = ttk.Label(self.device_frame, text="Proud Levá Fotodioda [mA]")
        label.grid(row=2, column=0, padx=GUIView.PADX,pady=GUIView.PADY, sticky="nsew")
        label = ttk.Label(self.device_frame, text="???")
        label.grid(row=2, column=1, padx=GUIView.PADX, pady=GUIView.PADY, sticky="nsew")
        self.measured_L_LED_current_label = label

        label = ttk.Label(self.device_frame, text="Proud Pravá Fotodioda [mA]")
        label.grid(row=2, column=2, padx=GUIView.PADX, pady=GUIView.PADY, sticky="nsew")
        label = ttk.Label(self.device_frame, text="???")
        label.grid(row=2, column=3, padx=GUIView.PADX, pady=GUIView.PADY, sticky="nsew")
        self.measured_R_LED_current_label = label


        # region outputs
        self.output_frame = ttk.LabelFrame(self, text="Výstupy")
        self.output_frame.grid(row=2, column=0, padx=GUIView.PADX, pady=GUIView.PADY, sticky="nsew")

        label = ttk.Label(self.output_frame, text="Odjistit/Zajistit")
        label.grid(row=0, column=0, padx=GUIView.PADX, pady=GUIView.PADY)
        label = ttk.Label(self.output_frame, text="???")
        label.grid(row=0, column=1, padx=GUIView.PADX, pady=GUIView.PADY)
        self.output_labels[Pins.BINDER] = label


        label = ttk.Label(self.output_frame, text="Vysunout/Zasunout")
        label.grid(row=1, column=0, padx=GUIView.PADX, pady=GUIView.PADY)
        label = ttk.Label(self.output_frame, text="???")
        label.grid(row=1, column=1, padx=GUIView.PADX, pady=GUIView.PADY)
        self.output_labels[Pins.AXIS_1] = label


        label = ttk.Label(self.output_frame, text="Stisknout/Uvolnit")
        label.grid(row=2, column=0, padx=GUIView.PADX, pady=GUIView.PADY)
        label = ttk.Label(self.output_frame, text="???")
        label.grid(row=2, column=1, padx=GUIView.PADX, pady=GUIView.PADY)
        self.output_labels[Pins.AXIS_2] = label
        # endregion outputs


        # region inputs
        self.input_frame = ttk.LabelFrame(self, text="Vstupy")
        self.input_frame.grid(row=2, column=1, padx=GUIView.PADX, pady=GUIView.PADY, sticky="nsew")

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
        # endregion inputs


        # self.camera_image_frame = ttk.Frame(self)
        # self.camera_image_frame.grid(row=3, column=0, columnspan=2, padx=GUIView.PADX, pady=GUIView.PADY, sticky="nsew")
        # self.image_label = tk.Label(self.camera_image_frame)
        # self.image_label.grid(row=0, column=0, sticky="nsew")


    def set_controller(self, controller: GUIController):
        self.controller = controller

    def create_custom_message_box(self):
        messagebox = tk.Toplevel(self.root)
        messagebox.title("Status zařízení")
        messagebox.configure(bg="#2a6138")

        # Create a custom frame with the desired text
        frame = tk.Frame(messagebox, bg="#2a6138")
        frame.grid(row=0, column=0, padx=20, pady=20)

        label = ttk.Label(frame, text="Zařízení bylo úspěšně zkontrolováno", background="#2a6138", foreground="white")
        label.grid(row=0, column=0, pady=10)
        # Center the custom_messagebox on the screen
        messagebox.geometry("+%d+%d" % (self.root.winfo_screenwidth() / 2 - 100, self.root.winfo_screenheight() / 2 - 50))
        self.message_box = messagebox


def create_root_window() -> tk.Tk:

    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    root = tk.Tk()
    root.title('SCILIF FINAL TESTER')
    root.tk.call("source", f"{ROOT_DIR}/../../../lib/theme/azure.tcl")
    root.tk.call("set_theme", "dark")

    # Set a minsize for the window, and place it in the middle
    root.update()
    root.minsize(root.winfo_width(), root.winfo_height())
    root.maxsize(root.winfo_screenwidth(), root.winfo_screenheight())
    x_coordinate = int((root.winfo_screenwidth() / 2) - (root.winfo_width() / 2))
    y_coordinate = int((root.winfo_screenheight() / 2) - (root.winfo_height() / 2))
    root.geometry(f"+{x_coordinate}+{y_coordinate - 20}")

    # w, h = root.winfo_screenwidth(), root.winfo_screenheight()
    # root.geometry("%dx%d+0+0" % (w, h-20))
    root.bind_all('<Control-c>', lambda _: root.destroy())
    return root



if __name__ == "__main__":

    logging.getLogger().setLevel(logging.INFO)
    root: tk.Tk = create_root_window()
    view = GUIView(root)
    root.mainloop()