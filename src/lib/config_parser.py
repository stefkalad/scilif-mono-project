from abc import abstractmethod
from configparser import ConfigParser


class CustomConfigParser:

    def __init__(self, config_path, firmware_section_name, overall_section_name="overall"):
        self.config_parser = ConfigParser()
        self.firmware_section_name = firmware_section_name
        self.overall_section_name = overall_section_name
        self.parse_config(config_path)

    def get(self, config_section, config_parameter):
        return self.config_parser.get(config_section, config_parameter)

    @abstractmethod
    def parse_config(self, config_path):
        pass


class FinalTesterConfig(CustomConfigParser):

    def parse_config(self, config_path):
        self.config_parser.read(config_path)


        self.overall_current = (
            int(self.get(self.firmware_section_name, "overall_current_lsl")),
            int(self.get(self.firmware_section_name, "overall_current_target")),
            int(self.get(self.firmware_section_name, "overall_current_usl"))
        )

        self.l_photo_current = (
            int(self.get(self.firmware_section_name, "l_photo_current_lsl")),
            int(self.get(self.firmware_section_name, "l_photo_current_target")),
            int(self.get(self.firmware_section_name, "l_photo_current_usl"))
        )

        self.r_photo_current = (
            int(self.get(self.firmware_section_name, "r_photo_current_lsl")),
            int(self.get(self.firmware_section_name, "r_photo_current_target")),
            int(self.get(self.firmware_section_name, "r_photo_current_usl"))
        )

    def __str__(self):
        return f'''FinalTesterConfig(
            overall_current={self.overall_current},
            l_photo_current={self.l_photo_current},
            r_photo_current={self.r_photo_current},
            )'''


class CNCProgrammerConfig(CustomConfigParser):

    def __init__(self, config_path, firmware_section_name, plate_section_name, overall_section_name="overall"):
        self.plate_section_name = plate_section_name
        super().__init__(config_path, firmware_section_name, overall_section_name)

    def parse_config(self, config_path):
        self.config_parser.read(config_path)

        # parse overall section
        self.pickle_default_path = self.get(self.overall_section_name, "pickle_default_path")
        self.firmware_default_path = self.get(self.overall_section_name, "firmware_default_path")

        # parse plate section
        self.plate_rows = int(self.get(self.plate_section_name, "rows"))
        self.plate_columns = int(self.get(self.plate_section_name, "columns"))
        self.plate_x_offset = int(self.get(self.plate_section_name, "x_offset_mm"))
        self.plate_y_offset = int(self.get(self.plate_section_name, "y_offset_mm"))
        self.plate_x_space = int(self.get(self.plate_section_name, "x_space_mm"))
        self.plate_y_space = int(self.get(self.plate_section_name, "y_space_mm"))
        self.dsp_height = int(self.get(self.plate_section_name, "dsp_height_mm"))
        self.dsp_width = int(self.get(self.plate_section_name, "dsp_width_mm"))


        # parse firmware section
        self.button_led_mode_change_duration = int(self.get(self.firmware_section_name, "button_led_mode_change_duration"))

        self.led_current_mode1 = (
            int(self.get(self.firmware_section_name, "led_current_mode1_lsl")),
            int(self.get(self.firmware_section_name, "led_current_mode1_target")),
            int(self.get(self.firmware_section_name, "led_current_mode1_usl")),
        )

        self.led_current_mode2 = (
            int(self.get(self.firmware_section_name, "led_current_mode2_lsl")),
            int(self.get(self.firmware_section_name, "led_current_mode2_target")),
            int(self.get(self.firmware_section_name, "led_current_mode2_usl")),
        )

    def __str__(self):
        return f'''CNCProgrammerConfig(
                pickle_default_path={self.pickle_default_path},
                firmware_default_path={self.firmware_default_path},
                plate: 
                [
                    rows={self.plate_rows},
                    columns={self.plate_columns},
                    DSP height [mm] ={self.dsp_height},
                    DSP width [mm] ={self.dsp_width},
                    space in X [mm] ={self.plate_x_space},
                    space in Y [mm] ={self.plate_y_space},
                    offset in X [mm] ={self.plate_x_offset},
                    offset in Y [mm] ={self.plate_y_offset}
                ]
                firmware: 
                [
                    led_current_mode1={self.led_current_mode1},
                    led_current_mode2={self.led_current_mode2},
                    button_led_mode_change_duration={self.button_led_mode_change_duration}
                ]
            )'''
