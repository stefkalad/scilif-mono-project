#!/usr/bin/python
from __future__ import annotations

import getopt
import logging
import sys
import tkinter as tk

from app.cnc_programmer.cnc_runner import CNCRunner
from app.cnc_programmer.gui.gui_controller import GUIController
from app.cnc_programmer.gui.gui_view import create_root_window, GUIView


def run():
    try:
        # initialize CNC runner
        cnc_runner = CNCRunner()

        # initialize GUI
        root: tk.Tk = create_root_window()
        view = GUIView(root)
        view.pack(fill=tk.BOTH, expand=1)

        controller = GUIController(view, cnc_runner)
        view.set_controller(controller)

        # set controllers
        view.set_controller(controller)
        cnc_runner.set_controller(controller)

        root.update()

        # run
        cnc_runner.start()
        root.mainloop()
    except KeyboardInterrupt:
        logging.debug("Keyboard interrupt catched")
        sys.stdout.flush()


def main(argv):
    logging.getLogger().setLevel(logging.DEBUG)
    try:
        opts, args = getopt.getopt(argv, "hd", ["--help", "debug"])
    except getopt.GetoptError:
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-d", "--debug"):
            logging.getLogger().setLevel(logging.DEBUG)

    run()


if __name__ == "__main__":
    print(sys.argv)
    main(sys.argv[1:])
