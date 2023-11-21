import logging
import time
from subprocess import PIPE, run, CalledProcessError, CompletedProcess

from app.cnc_programmer.rpi_board import RPiBoard


class DPSProgrammer:
    ERASE_COMMAND = "blank"
    LOAD_COMMAND = "program"

    def __init__(self) -> None:
        self.pickle_path: str = ''
        self.firmware_path: str = ''
        self.set_config()

    def set_config(self, pickle_path="~/.local/bin/n14", firmware_path="./resources/app.hex"):
        self.pickle_path = pickle_path
        self.firmware_path = firmware_path

    def erase(self) -> CompletedProcess:
        erase_cmd: str = self._erase_cmd()
        logging.info(f"Executing ERASE with cmd: {erase_cmd}")
        return self._execute(erase_cmd)

    def load(self) -> CompletedProcess:
        load_cmd: str = self._load_cmd()
        logging.info(f"Executing LOAD with cmd: {load_cmd}")
        return self._execute(load_cmd)

    def _erase_cmd(self) -> str:
        return f'{self.pickle_path} {DPSProgrammer.ERASE_COMMAND}'

    def _load_cmd(self, erase=1) -> str:
        return f'{self.pickle_path} {DPSProgrammer.LOAD_COMMAND} {self.firmware_path} {erase}'

    def _execute(self, command: str) -> CompletedProcess:
        try:
            completed_process: CompletedProcess = run(command, shell=True, stdout=PIPE, stderr=PIPE, universal_newlines=True)
            logging.info(f"Process exit code: {completed_process.returncode}, output: {completed_process.stdout}")
            return completed_process
        except CalledProcessError as e:
            logging.info(f"Process FAILED with exit code: {e.returncode}, output: {e.stderr}")



def test():
    print("Programming")
    board = RPiBoard()
    board.dps_power_supply_pin.value = False
    time.sleep(0.01)
    programmer = DPSProgrammer()
    cp = programmer.load()
    print(cp.returncode)
    print(cp.stdout)
    print(cp.stderr)
    board.dps_power_supply_pin.value = True


if __name__ == "__main__":
    test()
