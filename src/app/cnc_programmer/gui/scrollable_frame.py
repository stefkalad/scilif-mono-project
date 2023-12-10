from __future__ import annotations

import tkinter as tk
from tkinter import BOTH, LEFT, RIGHT, Y, DISABLED, NORMAL, ttk


class CustomFullScreenFrame(ttk.Frame):

    def __init__(self, root: tk.Tk) -> None:
        super().__init__(root)
        self.root = root

        # Create an exit button in the top right corner
        self.exit_button = ttk.Button(root, text="Ukončit", command=root.destroy)
        self.exit_button.place(x=root.winfo_screenwidth() - 80, y=10, width=80, height=30)

        # Set the root window to full screen
        root.attributes('-fullscreen', True)

    def bind_close_window_cb(self, callback):
        self.root.protocol("WM_DELETE_WINDOW", callback)
        self.exit_button.config(command=callback)

    def bind_button_click_cb(self, button: ttk.Button, callback) -> None:
        button.config(command=callback)

    def set_button_state(self, button: ttk.Button, condition: bool, change_style: bool = True) -> None:
        self.enable_button(button, change_style) if condition else self.disable_button(button)

    def enable_button(self, button: ttk.Button, change_style=True) -> None:
        if str(button["state"]) != str(NORMAL):
            # logging.debug(f"[GUI]: Changing {button['text']} state to {NORMAL}")
            button.config(state=NORMAL, style="Accent.TButton" if change_style else "TButton")

    def disable_button(self, button: ttk.Button) -> None:
        if str(button["state"]) != str(DISABLED):
            # logging.debug(f"[GUI]: Changing {button['text']} state to {DISABLED}")
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
        # if the entry is disabled, the text can be changed only be reenabling it
        is_disabled: bool = str(entry["state"]) == str(DISABLED)
        if is_disabled:
            entry.config(state=NORMAL)
        entry.delete(0, tk.END)
        entry.insert(0, text)

        if is_disabled:
            entry.config(state=DISABLED)

    def set_tx_state(self, entry: tk.Text, condition: bool) -> None:
        entry.config(state=NORMAL if condition else DISABLED)

    def set_tx_text(self, entry: tk.Text, text: str) -> None:
        is_disabled: bool = str(entry["state"]) == str(DISABLED)
        if is_disabled:
            entry.config(state=NORMAL)
        entry.insert(tk.END, text)
        if is_disabled:
            entry.config(state=DISABLED)
    def clear_tx_text(self, entry: tk.Text) -> None:
        is_disabled: bool = str(entry["state"]) == str(DISABLED)
        if is_disabled:
            entry.config(state=NORMAL)
        entry.delete(1.0, tk.END)
        if is_disabled:
            entry.config(state=DISABLED)




class EmbeddedScrollableFrame(ttk.Frame):

    def __init__(self, parent: ttk.Frame) -> None:
        super().__init__(parent)

        # Create a canvas and a scrollbar
        self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, )
        self.canvas = tk.Canvas(self, yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.canvas.yview)

        # Configure the canvas for scrolling
        self.scrollable_frame = tk.Frame(self.canvas)
        self.scrollable_frame_id = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor=tk.NW)


        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=1)

        self.canvas.bind_all("<MouseWheel>", self.scroll)
        self.canvas.bind_all("<Button-4>", self.scroll)
        self.canvas.bind_all("<Button-5>", self.scroll)

        # self.scrollable_frame.bind("<Configure>", lambda _: self.configure())
        self.scrollable_frame.bind('<Configure>', self._configure_interior)
        self.canvas.bind('<Configure>', self._configure_canvas)


    # track changes to the canvas and frame width and sync them, also updating the scrollbar
    def _configure_interior(self, event):
        # update the scrollbars to match the size of the inner frame
        size = (self.scrollable_frame.winfo_reqwidth(), self.scrollable_frame.winfo_reqheight())
        # print("Interior:", (0, 0, size[0], size[1]))

        # update the canvas's width to fit the inner frame
        self.canvas.config(scrollregion=(0, 0, size[0], size[1]))

        if self.scrollable_frame.winfo_reqwidth() != self.canvas.winfo_width():
            self.canvas.config(width=self.scrollable_frame.winfo_reqwidth())

    def _configure_canvas(self, event):
        # update the inner frame's width to fill the canvas
        if self.scrollable_frame.winfo_reqwidth() != self.canvas.winfo_width():
            # print("Canvas:", self.scrollable_frame.winfo_reqwidth(), self.canvas.winfo_width())
            self.canvas.itemconfigure(self.scrollable_frame_id, width=self.canvas.winfo_width())


    # def configure(self):
    #     print(self.canvas.bbox("all"), self.scrollable_frame.winfo_reqwidth(), self.canvas.winfo_width())
    #     self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    #     self.canvas.config(width=self.scrollable_frame.winfo_reqwidth())
    #     self.canvas.itemconfigure(self.scrollable_frame_id, width=self.canvas.winfo_width())

    def scroll(self, event):
        if self.canvas.bbox("all")[3] <= self.scrollable_frame.winfo_reqwidth():
            pass
        else:
            self.canvas.yview_scroll(-1 if event.num == 4 else +1 if event.num == 5 else 0, "units")

