from app.cnc_programmer.config.config import CNCProgrammerConfig
from app.cnc_programmer.config.firmware import FirmwareConfig
from app.cnc_programmer.config.plate import PlateConfig
from lib.config_parser import CustomConfigParser


class CNCProgrammerConfigParser(CustomConfigParser):

    def __init__(self, config_path):
        super().__init__(config_path)

    def parse_config(self) -> CNCProgrammerConfig:
        # parse firmware sections
        firmware_configs: dict[str, FirmwareConfig] = {}
        for section_name in self.get_all_sections_starting_with(CustomConfigParser.FIRMWARE_SECTION_PREFIX):
            firmware_configs[section_name.split(CustomConfigParser.FIRMWARE_SECTION_PREFIX)[1]] = self.parse_firmware_config(section_name)

        # parse plate sections
        plate_configs: dict[str, PlateConfig] = {}
        for section_name in self.get_all_sections_starting_with(CustomConfigParser.PLATE_SECTION_PREFIX):
            plate_configs[section_name.split(CustomConfigParser.PLATE_SECTION_PREFIX)[1]] = self.parse_plate_config(section_name)

        return CNCProgrammerConfig(
            self.get(CustomConfigParser.OVERALL_SECTION_NAME, "pickle_default_path"),
            self.get(CustomConfigParser.OVERALL_SECTION_NAME, "firmware_default_path"),
            firmware_configs,
            plate_configs)


    def parse_firmware_config(self, section_name: str) -> FirmwareConfig:
        assert section_name.startswith(CustomConfigParser.FIRMWARE_SECTION_PREFIX)

        return FirmwareConfig(
            section_name.split(CustomConfigParser.FIRMWARE_SECTION_PREFIX)[1],
            int(self.get(section_name, "button_led_mode_change_duration")),
            (
                int(self.get(section_name, "led_current_mode1_lsl")),
                int(self.get(section_name, "led_current_mode1_usl")),
            ),
            (
                int(self.get(section_name, "led_current_mode2_lsl")),
                int(self.get(section_name, "led_current_mode2_usl")),
            ),
            (
                int(self.get(section_name, "button_led_voltage_lsl")),
                int(self.get(section_name, "button_led_voltage_usl")),
            )

        )

    def parse_plate_config(self, section_name: str) -> PlateConfig:
        assert section_name.startswith(CustomConfigParser.PLATE_SECTION_PREFIX)

        return PlateConfig(
            section_name.split(CustomConfigParser.PLATE_SECTION_PREFIX)[1],
            int(self.get(section_name, "columns")),
            int(self.get(section_name, "rows")),
            int(self.get(section_name, "x_offset_mm")),
            int(self.get(section_name, "y_offset_mm")),
            float(self.get(section_name, "x_spacing_mm")),
            float(self.get(section_name, "y_spacing_mm")),
        )
