from abc import abstractmethod
from configparser import ConfigParser


class CustomConfigParser:

    def __init__(self, config_path, config_product_section, config_overall_section="overall"):
        self.config_parser = ConfigParser()
        self.parse_config(config_path, config_product_section, config_overall_section)

    def get(self, config_section, config_parameter):
        return self.config_parser.get(config_section, config_parameter)

    @abstractmethod
    def parse_config(self, config_path, config_product_section, config_overall_section):
        pass


class FinalTesterConfig(CustomConfigParser):

    def parse_config(self, config_path, config_product_section, config_overall_section):
        self.config_parser.read(config_path)


        self.overall_current = (
            int(self.get(config_product_section, "overall_current_lsl")),
            int(self.get(config_product_section, "overall_current_target")),
            int(self.get(config_product_section, "overall_current_usl"))
        )

        self.l_photo_current = (
            int(self.get(config_product_section, "l_photo_current_lsl")),
            int(self.get(config_product_section, "l_photo_current_target")),
            int(self.get(config_product_section, "l_photo_current_usl"))
        )

        self.r_photo_current = (
            int(self.get(config_product_section, "r_photo_current_lsl")),
            int(self.get(config_product_section, "r_photo_current_target")),
            int(self.get(config_product_section, "r_photo_current_usl"))
        )

    def __str__(self):
        return f'''FinalTesterConfig(
            overall_current={self.overall_current},
            l_photo_current={self.l_photo_current},
            r_photo_current={self.r_photo_current},
            )'''


class CNCProgrammerConfig(CustomConfigParser):

    def parse_config(self, config_path, config_product_section, config_overall_section):
        self.config_parser.read(config_path)

        self.pickle_default_path = self.get(config_overall_section, "pickle_default_path")
        self.firmware_default_path = self.get(config_overall_section, "firmware_default_path")

        self.button_led_mode_change_duration = int(self.get(config_product_section, "button_led_mode_change_duration"))

        self.led_current_mode1 = (
            int(self.get(config_product_section, "led_current_mode1_lsl")),
            int(self.get(config_product_section, "led_current_mode1_target")),
            int(self.get(config_product_section, "led_current_mode1_usl")),
        )

        self.led_current_mode2 = (
            int(self.get(config_product_section, "led_current_mode2_lsl")),
            int(self.get(config_product_section, "led_current_mode2_target")),
            int(self.get(config_product_section, "led_current_mode2_usl")),
        )

    def __str__(self):
        return f'''CNCProgrammerConfig(
            pickle_default_path={self.pickle_default_path}
            firmware_default_path={self.firmware_default_path}
            led_current_mode1={self.led_current_mode1},
            led_current_mode2={self.led_current_mode2},
            button_led_mode_change_duration={self.button_led_mode_change_duration}
            )'''
