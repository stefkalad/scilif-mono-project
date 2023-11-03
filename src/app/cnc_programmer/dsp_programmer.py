import os

from app.cnc_programmer.rpi_board import RPiBoard


class DspProgrammer:
    ERASE_COMMAND = "blank"
    LOAD_COMMAND = "program"

    def __init__(self, pickle_path="~/.local/bin/n14", firmware_path="./resources/app.hex") -> None:
        self.pickle_path = pickle_path
        self.firmware_path = firmware_path

    def erase(self) -> bool:
        cmd = f'{self.pickle_path} {DspProgrammer.ERASE_COMMAND}'
        exit_code: int = os.system(cmd)  # returns the exit status
        print(f"Erase done, exit code: {exit_code}")
        return exit_code == 0

    def load(self, erase=1) -> bool:
        cmd = f'{self.pickle_path} {DspProgrammer.LOAD_COMMAND} {self.firmware_path} {erase}'
        exit_code: int = os.system(cmd)  # returns the exit status
        print(f"Load done, exit code: {exit_code}")
        return exit_code == 0



def test():
    board = RPiBoard()
    board.dsp_power_supply_pin.value = False
    programmer = DspProgrammer()
    programmer.load()
    board.dsp_power_supply_pin.value = True


if __name__ == "__main__":
    test()
