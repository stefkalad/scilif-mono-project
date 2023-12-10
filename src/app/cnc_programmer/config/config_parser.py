from app.cnc_programmer.config.config import CNCProgrammerConfig
from app.cnc_programmer.config.firmware import FirmwareConfig
from app.cnc_programmer.config.plate import PlateConfig
from app.cnc_programmer.dps_mode import FirmwareType
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
            int(self.get(CustomConfigParser.OVERALL_SECTION_NAME, "z_moving_height_mm")),
            int(self.get(CustomConfigParser.OVERALL_SECTION_NAME, "z_minimum_safe_height_mm")),
            firmware_configs,
            plate_configs)


    def parse_firmware_config(self, section_name: str) -> FirmwareConfig:
        assert section_name.startswith(CustomConfigParser.FIRMWARE_SECTION_PREFIX)

        return FirmwareConfig(
            section_name.split(CustomConfigParser.FIRMWARE_SECTION_PREFIX)[1],
            self.get(section_name, "path"),
            FirmwareType(self.get(section_name, "type")),
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
            ),
            (
                int(self.get(section_name, "r_feedback_voltage_lsl")),
                int(self.get(section_name, "r_feedback_voltage_usl")),
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
