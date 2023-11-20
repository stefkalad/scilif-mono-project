from app.cnc_programmer.config.firmware import FirmwareConfig
from app.cnc_programmer.config.plate import PlateConfig


class CNCProgrammerConfig:

    def __init__(self, pickle_default_path: str, firmware_default_path: str, firmware_configs: dict[str, FirmwareConfig], plate_configs: dict[str, PlateConfig]):
        self._pickle_default_path: str = pickle_default_path
        self._firmware_default_path: str = firmware_default_path
        self._firmware_configs: dict[str, FirmwareConfig] = firmware_configs
        self._plate_configs: dict[str, PlateConfig] = plate_configs

    @property
    def firmware_default_path(self) -> str:
        return self._firmware_default_path

    @property
    def pickle_default_path(self) -> str:
        return self._pickle_default_path

    @property
    def firmware_configs(self) -> dict[str, FirmwareConfig]:
        return self._firmware_configs

    @property
    def plate_configs(self) -> dict[str, PlateConfig]:
        return self._plate_configs

    def __str__(self):
        return f'''CNCProgrammerConfig(
                pickle_default_path={self.pickle_default_path},
                firmware_default_path={self.firmware_default_path},
                plate_configs={self.plate_configs},
                firmware_configs ={self.firmware_configs}
            )'''



