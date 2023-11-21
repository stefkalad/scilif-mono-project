

class DPSLog:
    def __init__(self,
                 x=None, y=None,
                 operation_successful=None,
                 fw_uploaded=None, fw_upload_message=None,
                 led_current_mode1=None, led_current_mode1_passed=None,
                 led_current_mode2=None, led_current_mode2_passed=None,
                 button_led_voltage=None, button_led_voltage_passed=None) -> None:
        self._x: int = x
        self._y: int = y
        self._operation_successful: bool = operation_successful
        self._fw_uploaded: bool = fw_uploaded
        self._fw_upload_message: str = fw_upload_message
        self._led_current_mode1: float = led_current_mode1
        self._led_current_mode1_passed: bool = led_current_mode1_passed
        self._led_current_mode2: float = led_current_mode2
        self._led_current_mode2_passed: bool = led_current_mode2_passed
        self._button_led_voltage: float = button_led_voltage
        self._button_led_voltage_passed: bool = button_led_voltage_passed

    @property
    def x(self) -> int:
        return self._x

    @x.setter
    def x(self, value: int):
        self._x = value

    @property
    def y(self) -> int:
        return self._y

    @y.setter
    def y(self, value: int):
        self._y = value

    @property
    def fw_uploaded(self) -> bool:
        return self._fw_uploaded

    @fw_uploaded.setter
    def fw_uploaded(self, value: bool):
        self._fw_uploaded = value

    @property
    def fw_upload_message(self) -> str:
        return self._fw_upload_message

    @fw_upload_message.setter
    def fw_upload_message(self, value: str):
        self._fw_upload_message = value

    @property
    def led_current_mode1_passed(self) -> bool:
        return self._led_current_mode1_passed

    @led_current_mode1_passed.setter
    def led_current_mode1_passed(self, value: bool):
        self._led_current_mode1_passed = value

    @property
    def led_current_mode1(self) -> float:
        return self._led_current_mode1

    @led_current_mode1.setter
    def led_current_mode1(self, value: float):
        self._led_current_mode1 = value

    @property
    def led_current_mode2_passed(self) -> bool:
        return self._led_current_mode2_passed

    @led_current_mode2_passed.setter
    def led_current_mode2_passed(self, value: bool):
        self._led_current_mode2_passed = value

    @property
    def led_current_mode2(self) -> float:
        return self._led_current_mode2

    @led_current_mode2.setter
    def led_current_mode2(self, value: float):
        self._led_current_mode2 = value

    @property
    def button_led_voltage_passed(self) -> bool:
        return self._button_led_voltage_passed

    @button_led_voltage_passed.setter
    def button_led_voltage_passed(self, value: bool):
        self._button_led_voltage_passed = value

    @property
    def button_led_voltage(self) -> float:
        return self._button_led_voltage

    @button_led_voltage.setter
    def button_led_voltage(self, value: float):
        self._button_led_voltage = value

    @property
    def operation_successful(self):
        return self.fw_uploaded and self.led_current_mode1_passed and (self.led_current_mode2_passed if self.led_current_mode2 is not None else True) and self.button_led_voltage_passed

    def __str__(self):
        return f"Coordinates (x, y): ({self.x}, {self.y})\n" \
               f"Firmware Uploaded: {self.fw_uploaded}\n" \
               f"Firmware Upload Message: {self.fw_upload_message}\n" \
               f"LED Current Mode 1: {self.led_current_mode1} (Passed: {self.led_current_mode1_passed})\n" \
               f"LED Current Mode 2: {self.led_current_mode2} (Passed: {self.led_current_mode2_passed})\n" \
               f"Button LED Voltage: {self.button_led_voltage} (Passed: {self.button_led_voltage_passed})\n" \
               f"Operation Successful: {self.operation_successful}"




