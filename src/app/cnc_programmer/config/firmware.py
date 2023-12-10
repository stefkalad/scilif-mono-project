from app.cnc_programmer.dps_mode import FirmwareType


class FirmwareConfig:

    def __init__(self, name: str,
                 path: str,
                 type: FirmwareType,
                 button_led_mode_change_duration: int,
                 led_current_mode1: (int, int),
                 led_current_mode2: (int, int),
                 button_led_voltage: (int, int),
                 r_feedback_voltage: (int, int)):
        self.name: str = name
        self._path: str = path
        self._type: FirmwareType = type
        self._button_led_mode_change_duration: int = button_led_mode_change_duration
        self._led_current_mode1: (int, int) = led_current_mode1
        self._led_current_mode2: (int, int) = led_current_mode2
        self._button_led_voltage: (int, int) = button_led_voltage
        self._r_feedback_voltage: (int, int) = r_feedback_voltage


    @property
    def path(self) -> str:
        return self._path

    @property
    def type(self) -> FirmwareType:
        return self._type

    @property
    def button_led_mode_change_duration(self) -> int:
        return self._button_led_mode_change_duration

    @property
    def led_current_mode1(self) -> (int, int):
        return self._led_current_mode1

    @property
    def led_current_mode2(self) -> (int, int):
        return self._led_current_mode2

    @property
    def button_led_voltage(self) -> (int, int):
        return self._button_led_voltage

    @property
    def r_feedback_voltage(self) -> (int, int):
        return self._r_feedback_voltage

    def __str__(self) -> str:
        return f'''Firmware {self.name}: [
                    path = {self.path}
                    type = {self.type.value}
                    button_led_mode_change_duration = {self.button_led_mode_change_duration}
                    led_current_mode1 = {self.led_current_mode1},
                    led_current_mode2 = {self.led_current_mode2},
                    button_led_voltage = {self.button_led_voltage},
                    r_feedback_voltage = {self.r_feedback_voltage},
        ]'''
