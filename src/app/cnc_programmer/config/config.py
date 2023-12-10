from app.cnc_programmer.config.firmware import FirmwareConfig
from app.cnc_programmer.config.plate import PlateConfig


class CNCProgrammerConfig:

    def __init__(self, pickle_default_path: str, z_moving_height: int, z_minimum_safe_height: int, firmware_configs: dict[str, FirmwareConfig], plate_configs: dict[str, PlateConfig]):
        self._pickle_default_path: str = pickle_default_path
        self._z_moving_height_mm: int = z_moving_height
        self._z_minimum_safe_height_mm: int = z_minimum_safe_height
        self._firmware_configs: dict[str, FirmwareConfig] = firmware_configs
        self._plate_configs: dict[str, PlateConfig] = plate_configs

    @property
    def pickle_default_path(self) -> str:
        return self._pickle_default_path

    @property
    def z_moving_height_mm(self) -> int:
        return self._z_moving_height_mm

    @property
    def     z_minimum_safe_height_mm(self) -> int:
        return self._z_minimum_safe_height_mm

    @property
    def firmware_configs(self) -> dict[str, FirmwareConfig]:
        return self._firmware_configs

    @property
    def plate_configs(self) -> dict[str, PlateConfig]:
        return self._plate_configs

    def __str__(self):
        return f'''CNCProgrammerConfig(
                pickle_default_path={self.pickle_default_path},
                z_moving_height_mm={self.z_moving_height_mm},
                z_minimum_safe_height_mm={self.z_minimum_safe_height_mm},
                plate_configs={self.plate_configs},
                firmware_configs ={self.firmware_configs}
            )'''



