#!/usr/bin/python
from __future__ import annotations

import getopt
import logging
import sys
import tkinter as tk

from app.cnc_programmer.cnc_runner import CNCRunner
from app.cnc_programmer.gui.gui import GUIView, GUIController, create_root_window
from app.cnc_programmer.gui.scrollable_frame import ScrollableFrame


def run():
    try:

        # config: CNCProgrammerConfig = CNCProgrammerConfigParser(f"./theme/config_cnc_programmer.conf").parse_config()
        # logging.info(f"Loaded configuration: {config}")

        # initialize CNC runner
        cnc_runner = CNCRunner()
        cnc_runner.start()

        # initialize GUI

        root: tk.Tk = create_root_window()
        view = GUIView(root, ScrollableFrame(root))
        controller = GUIController(view, cnc_runner)

        # set controllers
        view.set_controller(controller)
        cnc_runner.set_controller(controller)

        # run
        root.update()
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
