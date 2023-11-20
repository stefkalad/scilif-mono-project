from configparser import ConfigParser
from typing import List


class CustomConfigParser:

    OVERALL_SECTION_NAME = "OVERALL"
    FIRMWARE_SECTION_PREFIX = "FW_"
    PLATE_SECTION_PREFIX = "PLATE_"

    def __init__(self, config_path: str) -> None:
        self.config_parser: ConfigParser = ConfigParser()
        self.config_path: str = config_path
        self.config_parser.read(self.config_path)

    def get(self, config_section: str, config_parameter: str) -> str:
        return self.config_parser.get(config_section, config_parameter)

    def get_all_sections_starting_with(self, section_prefix: str) -> List[str]:
        return list(filter(lambda s: s.startswith(section_prefix), self.config_parser.sections()))


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