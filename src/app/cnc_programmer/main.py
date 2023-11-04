#!/usr/bin/python
import logging
import getopt
import sys

from app.cnc_programmer.cnc_programmer import CNCProgrammer
# from .gui import run
from lib.config_parser import CNCProgrammerConfig



def run():
    try:
        config: CNCProgrammerConfig = CNCProgrammerConfig(f"./resources/config_cnc_programmer.conf", "firmware_thule_two_modes", "plate_thule_4332")
        print(config)
        cnc_programmer = CNCProgrammer(config)
        cnc_programmer.start_programming_dsp_plate()
        # cnc_programmer.process_dsp()

        # gui_run()
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


if __name__ == "__main__":
    print(sys.argv)
    main(sys.argv[1:])
