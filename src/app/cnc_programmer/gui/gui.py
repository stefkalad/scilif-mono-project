from __future__ import annotations

import tkinter as tk 
from tkinter import BOTH, BOTTOM, DISABLED, LEFT, NORMAL, RIGHT, TOP, X, Y, YES, ttk
from tkinter import filedialog


class Model:
    def __init__(self):
        self.config_data = {}
        self.config_path = ''

    def load_config(self, file_path):
        with open(file_path, "r") as config_file:
            config_data = config_file.read()
            # Parse the config data and update the model
            self.config_data = {}  # Replace with your parsing logic

    def get_config_data(self):
        return self.config_data

    def set_config_path(self, config_path):
        self.config_path = config_path



class View(ttk.Frame):
    FG_COLOR = "#eaf205"
    PADX = (15, 15)
    PADY = (15, 15)

    def __init__(self, root):
        self.root = root
        ttk.Frame.__init__(self)
        # super().__init__(root)

        # for index in [0, 1, 2]:
        #     self.columnconfigure(index=index, weight=1)
        #     self.rowconfigure(index=index, weight=1)
        

        self.label = ttk.Label(self, text="SCILIF CNC Programmer", justify="center", font=("-size", 16, "-weight", "bold"))
        # self.label.grid(row=0, column=0, pady=10, columnspan=2)
        
        self.config_frame = ttk.LabelFrame(self, text="Select Configuration", padding=(20, 10))
        self.config_frame.grid(row=1, column=0, padx=View.PADX, pady=View.PADY, sticky="nsew")
        

        self.config_label = ttk.Label(self.config_frame, text="Upload Config File:")
        self.config_label.grid(row=1, column=0, padx=View.PADX, pady=View.PADY, sticky="nsew")

        self.config_entry_text = tk.StringVar()
        self.config_entry = ttk.Entry(self.config_frame, textvariable=self.config_entry_text, state=DISABLED)
        self.config_entry.grid(row=1, column=1, columnspan=2, padx=View.PADX, pady=View.PADY, sticky="nsew")

        self.browse_files_button = ttk.Button(self.config_frame, text="Browse Files")
        self.browse_files_button.grid(row=1, column=3, padx=10, pady=10, sticky="nsew")

        self.upload_button = ttk.Button(self.config_frame, text="Upload", style="Accent.TButton")
        self.upload_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")



        self.product_frame = ttk.LabelFrame(self, text="Select Product", padding=(20, 10))
        # self.product_frame.pack(expand=YES, fill=BOTH)
        self.product_frame.grid(row=3, column=0, padx=(10, 10), pady=(10, 10), sticky="nsew")

        self.product_code_label = ttk.Label(self.product_frame, text="Product Code:")
        self.product_code_label.grid(row=3,column=0)

        self.product_code_entry = ttk.Entry(self.product_frame)
        self.product_code_entry.grid(row=3,column=1)




        self.settings_frame = ttk.LabelFrame(self, text="Settings", padding=(20, 10))
        self.settings_frame.grid(row=4, column=0, padx=(10, 10), pady=(10, 10), sticky="nsew")

        self.row_label, self.row_entry = self.generate_label_entry_pair(self.settings_frame, "Rows (M):", 4, 0)
        self.column_label, self.column_entry = self.generate_label_entry_pair(self.settings_frame, "Columns (N):", 4, 2)

        self.row_space_label, self.row_space_entry = self.generate_label_entry_pair(self.settings_frame, "Row space [mm]:", 5, 0)
        self.column_space_label, self.column_space_entry = self.generate_label_entry_pair(self.settings_frame, "Column space [mm]:", 5, 2)

        # self.settings_frame.pack(expand=YES, fill=BOTH)
        


        # self.start_button = tk.Button(root, text="START")
        # # self.start_button.grid(row=3,column=0)

        # self.pause_button = tk.Button(root, text="PAUSE")
        # self.pause_button.grid(row=3,column=1)

        # self.info_log_label = tk.Label(root, text="Information Log:", bg=SCILIF_BLACK, fg=SCILIF_YELLOW)

        # self.info_log_text = tk.Text(root, height=5, width=40, bg=SCILIF_BLACK, fg=SCILIF_YELLOW)

        # self.malfunction_log_label = tk.Label(root, text="Malfunction Log:", bg=SCILIF_BLACK, fg=SCILIF_YELLOW)

        # self.malfunction_log_text = tk.Text(root, height=5, width=40, bg=SCILIF_BLACK, fg=SCILIF_YELLOW)
        
    
    def set_controller(self, controller: Controller): 
        self.controller = controller
    
    def generate_label_entry_pair(self, frame, label_text, row, column) -> (ttk.Label, ttk.Entry):
        label = ttk.Label(frame, text=label_text)
        label.grid(row=row,column=column, padx=View.PADX, pady=View.PADY)
        entry = ttk.Entry(frame)
        entry.grid(row=row,column=column+1, padx=View.PADX, pady=View.PADY)
        return (label, entry)


    def bind_config_entry_focus_in_cb(self, callback):
        self.config_entry.bind("<FocusIn>", callback)

    def bind_upload_button_cb(self, callback):
        self.upload_button.config(command=callback)

    def bind_browse_files_button_cb(self, callback):
        self.browse_files_button.config(command=callback)

    # def bind_start_button_cb(self, callback):
    #     self.start_button.config(command=callback)

    # def bind_pause_button_cb(self, callback):
    #     self.pause_button.config(command=callback)

    # def update_info_log(self, text):
    #     self.info_log_text.insert(tk.END, text)

    # def update_malfunction_log(self, text):
    #     self.malfunction_log_text.insert(tk.END, text)


class Controller:
    def __init__(self, model: Model, view: View):
        self.model = model
        self.view = view

        self.is_running = False

        # Initial setup
        self.view.upload_button.config(state=DISABLED)

        # Bind callbacks
        self.view.bind_upload_button_cb(self.upload_config)
        self.view.bind_browse_files_button_cb(self.browse_files)
        # self.view.bind_start_button_cb(self.start)
        # self.view.bind_pause_button_cb(self.pause)


    def browse_files(self):
        root = self.view.root

        # fd = filedialog.FileDialog(root)
        # file_path = fd.go(pattern="*.conf")


        file_path = filedialog.askopenfilename(master=root,filetypes=[("Config Files", "*.conf")])
        if file_path and len(file_path):
            # update model
            self.model.load_config(file_path)
            self.model.set_config_path(file_path)
            
            # update view 
            self.view.config_entry_text.set(file_path)
            self.view.upload_button.config(state=NORMAL)

    def upload_config(self):

        print ("Upload...")

        



    def start(self):
        if not self.is_running:
            self.is_running = True
            self.view.update_info_log("Application started...\n")

    def pause(self):
        if self.is_running:
            self.is_running = False
            self.view.update_info_log("Application paused...\n")



    


def run():

    root = tk.Tk()
    root.title('Tkinter MVC Demo')
    root.tk.call("source", "azure.tcl")
    root.tk.call("set_theme", "dark")

    model = Model()
    view = View(root)
    view.pack(fill="both", expand=True)
    controller = Controller(model, view)
    view.set_controller(controller)


    # Set a minsize for the window, and place it in the middle
    root.update()
    root.minsize(root.winfo_width(), root.winfo_height())
    x_cordinate = int((root.winfo_screenwidth() / 2) - (root.winfo_width() / 2))
    y_cordinate = int((root.winfo_screenheight() / 2) - (root.winfo_height() / 2))
    root.geometry("+{}+{}".format(x_cordinate, y_cordinate-20))

    root.bind_all('<Control-c>', lambda _: root.destroy())
    root.mainloop()

    
    

class View2(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self)

        # Make the app responsive
        for index in [0, 1, 2]:
            self.columnconfigure(index=index, weight=1)
            self.rowconfigure(index=index, weight=1)

        # Create value lists
        self.option_menu_list = ["", "OptionMenu", "Option 1", "Option 2"]
        self.combo_list = ["Combobox", "Editable item 1", "Editable item 2"]
        self.readonly_combo_list = ["Readonly combobox", "Item 1", "Item 2"]

        # Create control variables
        self.var_0 = tk.BooleanVar()
        self.var_1 = tk.BooleanVar(value=True)
        self.var_2 = tk.BooleanVar()
        self.var_3 = tk.IntVar(value=2)
        self.var_4 = tk.StringVar(value=self.option_menu_list[1])
        self.var_5 = tk.DoubleVar(value=75.0)

        # Create widgets :)
        self.setup_widgets()

    def setup_widgets(self):
        # Create a Frame for the Checkbuttons
        self.check_frame = ttk.LabelFrame(self, text="Checkbuttons", padding=(20, 10))
        self.check_frame.grid(
            row=0, column=0, padx=(20, 10), pady=(20, 10), sticky="nsew"
        )

        # Checkbuttons
        self.check_1 = ttk.Checkbutton(
            self.check_frame, text="Unchecked", variable=self.var_0
        )
        self.check_1.grid(row=0, column=0, padx=5, pady=10, sticky="nsew")

        self.check_2 = ttk.Checkbutton(
            self.check_frame, text="Checked", variable=self.var_1
        )
        self.check_2.grid(row=1, column=0, padx=5, pady=10, sticky="nsew")

        self.check_3 = ttk.Checkbutton(
            self.check_frame, text="Third state", variable=self.var_2
        )
        self.check_3.state(["alternate"])
        self.check_3.grid(row=2, column=0, padx=5, pady=10, sticky="nsew")

        self.check_4 = ttk.Checkbutton(
            self.check_frame, text="Disabled", state="disabled"
        )
        self.check_4.state(["disabled !alternate"])
        self.check_4.grid(row=3, column=0, padx=5, pady=10, sticky="nsew")

        # Separator
        self.separator = ttk.Separator(self)
        self.separator.grid(row=1, column=0, padx=(20, 10), pady=10, sticky="ew")

        # Create a Frame for the Radiobuttons
        self.radio_frame = ttk.LabelFrame(self, text="Radiobuttons", padding=(20, 10))
        self.radio_frame.grid(row=2, column=0, padx=(20, 10), pady=10, sticky="nsew")

        # Radiobuttons
        self.radio_1 = ttk.Radiobutton(
            self.radio_frame, text="Unselected", variable=self.var_3, value=1
        )
        self.radio_1.grid(row=0, column=0, padx=5, pady=10, sticky="nsew")
        self.radio_2 = ttk.Radiobutton(
            self.radio_frame, text="Selected", variable=self.var_3, value=2
        )
        self.radio_2.grid(row=1, column=0, padx=5, pady=10, sticky="nsew")
        self.radio_4 = ttk.Radiobutton(
            self.radio_frame, text="Disabled", state="disabled"
        )
        self.radio_4.grid(row=3, column=0, padx=5, pady=10, sticky="nsew")

        # Create a Frame for input widgets
        self.widgets_frame = ttk.Frame(self, padding=(0, 0, 0, 10))
        self.widgets_frame.grid(
            row=0, column=1, padx=10, pady=(30, 10), sticky="nsew", rowspan=3
        )
        self.widgets_frame.columnconfigure(index=0, weight=1)

        # Entry
        self.entry = ttk.Entry(self.widgets_frame)
        self.entry.insert(0, "Entry")
        self.entry.grid(row=0, column=0, padx=5, pady=(0, 10), sticky="ew")

        # Spinbox
        self.spinbox = ttk.Spinbox(self.widgets_frame, from_=0, to=100, increment=0.1)
        self.spinbox.insert(0, "Spinbox")
        self.spinbox.grid(row=1, column=0, padx=5, pady=10, sticky="ew")

        # Combobox
        self.combobox = ttk.Combobox(self.widgets_frame, values=self.combo_list)
        self.combobox.current(0)
        self.combobox.grid(row=2, column=0, padx=5, pady=10, sticky="ew")

        # Read-only combobox
        self.readonly_combo = ttk.Combobox(
            self.widgets_frame, state="readonly", values=self.readonly_combo_list
        )
        self.readonly_combo.current(0)
        self.readonly_combo.grid(row=3, column=0, padx=5, pady=10, sticky="ew")

        # Menu for the Menubutton
        self.menu = tk.Menu(self)
        self.menu.add_command(label="Menu item 1")
        self.menu.add_command(label="Menu item 2")
        self.menu.add_separator()
        self.menu.add_command(label="Menu item 3")
        self.menu.add_command(label="Menu item 4")

        # Menubutton
        self.menubutton = ttk.Menubutton(
            self.widgets_frame, text="Menubutton", menu=self.menu, direction="below"
        )
        self.menubutton.grid(row=4, column=0, padx=5, pady=10, sticky="nsew")

        # OptionMenu
        self.optionmenu = ttk.OptionMenu(
            self.widgets_frame, self.var_4, *self.option_menu_list
        )
        self.optionmenu.grid(row=5, column=0, padx=5, pady=10, sticky="nsew")

        # Button
        self.button = ttk.Button(self.widgets_frame, text="Button")
        self.button.grid(row=6, column=0, padx=5, pady=10, sticky="nsew")

        # Accentbutton
        self.accentbutton = ttk.Button(
            self.widgets_frame, text="Accent button", style="Accent.TButton"
        )
        self.accentbutton.grid(row=7, column=0, padx=5, pady=10, sticky="nsew")

        # Togglebutton
        self.togglebutton = ttk.Checkbutton(
            self.widgets_frame, text="Toggle button", style="Toggle.TButton"
        )
        self.togglebutton.grid(row=8, column=0, padx=5, pady=10, sticky="nsew")

        # Switch
        self.switch = ttk.Checkbutton(
            self.widgets_frame, text="Switch", style="Switch.TCheckbutton"
        )
        self.switch.grid(row=9, column=0, padx=5, pady=10, sticky="nsew")

        # Panedwindow
        self.paned = ttk.PanedWindow(self)
        self.paned.grid(row=0, column=2, pady=(25, 5), sticky="nsew", rowspan=3)

        # Pane #1
        self.pane_1 = ttk.Frame(self.paned, padding=5)
        self.paned.add(self.pane_1, weight=1)

        # Scrollbar
        self.scrollbar = ttk.Scrollbar(self.pane_1)
        self.scrollbar.pack(side="right", fill="y")

        # Treeview
        self.treeview = ttk.Treeview(
            self.pane_1,
            selectmode="browse",
            yscrollcommand=self.scrollbar.set,
            columns=(1, 2),
            height=10,
        )
        self.treeview.pack(expand=True, fill="both")
        self.scrollbar.config(command=self.treeview.yview)

        # Treeview columns
        self.treeview.column("#0", anchor="w", width=120)
        self.treeview.column(1, anchor="w", width=120)
        self.treeview.column(2, anchor="w", width=120)

        # Treeview headings
        self.treeview.heading("#0", text="Column 1", anchor="center")
        self.treeview.heading(1, text="Column 2", anchor="center")
        self.treeview.heading(2, text="Column 3", anchor="center")

        # Define treeview data
        treeview_data = [
            ("", 1, "Parent", ("Item 1", "Value 1")),
            (1, 2, "Child", ("Subitem 1.1", "Value 1.1")),
            (1, 3, "Child", ("Subitem 1.2", "Value 1.2")),
            (1, 4, "Child", ("Subitem 1.3", "Value 1.3")),
            (1, 5, "Child", ("Subitem 1.4", "Value 1.4")),
            ("", 6, "Parent", ("Item 2", "Value 2")),
            (6, 7, "Child", ("Subitem 2.1", "Value 2.1")),
            (6, 8, "Sub-parent", ("Subitem 2.2", "Value 2.2")),
            (8, 9, "Child", ("Subitem 2.2.1", "Value 2.2.1")),
            (8, 10, "Child", ("Subitem 2.2.2", "Value 2.2.2")),
            (8, 11, "Child", ("Subitem 2.2.3", "Value 2.2.3")),
            (6, 12, "Child", ("Subitem 2.3", "Value 2.3")),
            (6, 13, "Child", ("Subitem 2.4", "Value 2.4")),
            ("", 14, "Parent", ("Item 3", "Value 3")),
            (14, 15, "Child", ("Subitem 3.1", "Value 3.1")),
            (14, 16, "Child", ("Subitem 3.2", "Value 3.2")),
            (14, 17, "Child", ("Subitem 3.3", "Value 3.3")),
            (14, 18, "Child", ("Subitem 3.4", "Value 3.4")),
            ("", 19, "Parent", ("Item 4", "Value 4")),
            (19, 20, "Child", ("Subitem 4.1", "Value 4.1")),
            (19, 21, "Sub-parent", ("Subitem 4.2", "Value 4.2")),
            (21, 22, "Child", ("Subitem 4.2.1", "Value 4.2.1")),
            (21, 23, "Child", ("Subitem 4.2.2", "Value 4.2.2")),
            (21, 24, "Child", ("Subitem 4.2.3", "Value 4.2.3")),
            (19, 25, "Child", ("Subitem 4.3", "Value 4.3")),
        ]

        # Insert treeview data
        for item in treeview_data:
            self.treeview.insert(
                parent=item[0], index="end", iid=item[1], text=item[2], values=item[3]
            )
            if item[0] == "" or item[1] in {8, 21}:
                self.treeview.item(item[1], open=True)  # Open parents

        # Select and scroll
        self.treeview.selection_set(10)
        self.treeview.see(7)

        # Notebook, pane #2
        self.pane_2 = ttk.Frame(self.paned, padding=5)
        self.paned.add(self.pane_2, weight=3)

        # Notebook, pane #2
        self.notebook = ttk.Notebook(self.pane_2)
        self.notebook.pack(fill="both", expand=True)

        # Tab #1
        self.tab_1 = ttk.Frame(self.notebook)
        for index in [0, 1]:
            self.tab_1.columnconfigure(index=index, weight=1)
            self.tab_1.rowconfigure(index=index, weight=1)
        self.notebook.add(self.tab_1, text="Tab 1")

        # Scale
        self.scale = ttk.Scale(
            self.tab_1,
            from_=100,
            to=0,
            variable=self.var_5,
            command=lambda event: self.var_5.set(self.scale.get()),
        )
        self.scale.grid(row=0, column=0, padx=(20, 10), pady=(20, 0), sticky="ew")

        # Progressbar
        self.progress = ttk.Progressbar(
            self.tab_1, value=0, variable=self.var_5, mode="determinate"
        )
        self.progress.grid(row=0, column=1, padx=(10, 20), pady=(20, 0), sticky="ew")

        # Label
        self.label = ttk.Label(
            self.tab_1,
            text="Azure theme for ttk",
            justify="center",
            font=("-size", 15, "-weight", "bold"),
        )
        self.label.grid(row=1, column=0, pady=10, columnspan=2)

        # Tab #2
        self.tab_2 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_2, text="Tab 2")

        # Tab #3
        self.tab_3 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_3, text="Tab 3")

        # Sizegrip
        self.sizegrip = ttk.Sizegrip(self)
        self.sizegrip.grid(row=100, column=100, padx=(0, 5), pady=(0, 5))

    

if __name__ == "__main__":
    run()

