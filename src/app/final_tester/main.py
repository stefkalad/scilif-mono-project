import logging
import getopt
import sys
import tkinter as tk

from app.final_tester.gui.gui import create_root_window, GUIView, GUIController
from app.final_tester.final_tester import FinalTester


def run():
    try:
        final_tester = FinalTester()

        root: tk.Tk = create_root_window()
        view = GUIView(root)
        controller = GUIController(view, final_tester)
        # set controller
        view.set_controller(controller)
        final_tester.set_controller(controller)

        # run final tester in a separate thread
        final_tester.start()
        # run GUI
        root.mainloop()

    except KeyboardInterrupt:
        logging.debug("Keyboard interrupt catched")
        sys.stdout.flush()


def main(argv):
    logging.getLogger().setLevel(logging.INFO)
    try:
        opts, args = getopt.getopt(argv, "hd", ["--help", "debug"])
    except getopt.GetoptError:
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-d", "--debug"):
            logging.getLogger().setLevel(logging.DEBUG)

    run()