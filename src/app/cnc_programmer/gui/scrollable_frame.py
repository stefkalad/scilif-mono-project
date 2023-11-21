
import tkinter as tk
from tkinter import BOTH, LEFT, RIGHT, VERTICAL, Y, ttk


class ScrollableFrame(ttk.Frame):

    def __init__(self, root: tk.Tk) -> None:
        # Create a main frame
        main_frame = ttk.Frame(root)
        main_frame.pack(fill=BOTH, expand=1)

        # Create a canvas and a scrollbar
        canvas = tk.Canvas(main_frame)
        canvas.pack(side=LEFT, fill=BOTH, expand=1)
        scrollbar = ttk.Scrollbar(main_frame, orient=VERTICAL, command=canvas.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind("<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all")))

        # Create a frame within the canvas to hold the widgets
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        super().__init__(canvas)
        canvas.create_window((screen_width / 2, screen_height / 2), window=self, anchor="center")

        root.bind("<Button-4>", self.scroll)
        root.bind("<Button-5>", self.scroll)

        # Create an exit button in the top right corner
        exit_button = ttk.Button(root, text="Ukončit", command=root.destroy)
        exit_button.place(x=screen_width - 80, y=10, width=80, height=30)
        # Set the root window to full screen
        root.attributes('-fullscreen', True)

        self.canvas: tk.Canvas = canvas
        self.exit_button = exit_button

    def scroll(self, event):
        self.canvas.yview_scroll(-1 if event.num == 4 else +1 if event.num == 5 else 0, "units")

