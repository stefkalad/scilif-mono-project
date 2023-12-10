from app.cnc_programmer.config.firmware import FirmwareConfig
from app.cnc_programmer.dps_log import DPSLog
from app.cnc_programmer.dps_mode import FirmwareType


class MessagesFormatter:

    @staticmethod
    def format_dps_ok_msg(config: FirmwareConfig, dps_log: DPSLog) -> str:
        return (f"[programování]: Nahráno - {config.path.split('/')[-1]}\n" +
                f"[testování]: Proud LED (mód 1) - {dps_log.led_current_mode1} mA\n" +
                f"[testování]: Napětí LED tlačítka - {dps_log.button_led_voltage} mV\n" +
                f"[testování]: Napětí ZV rezistoru - {dps_log.r_feedback_voltage} mV\n")

    @staticmethod
    def format_dps_error_msg(config: FirmwareConfig, dps_log: DPSLog) -> str:
        if not dps_log.fw_uploaded:
            return MessagesFormatter.format_fw_upload_error_msg(dps_log)
        else:
            message: str = ''
            if not dps_log.led_current_mode1_passed:
                message += MessagesFormatter.format_led_current_error_msg(config, dps_log, 1)
            if config.type == FirmwareType.FLASH and not dps_log.led_current_mode2_passed:
                message += MessagesFormatter.format_led_current_error_msg(config, dps_log, 2)
            if not dps_log.button_led_voltage_passed:
                message += MessagesFormatter.format_button_led_voltage_error_msg(config, dps_log)
            if not dps_log.r_feedback_voltage_passed:
                message += MessagesFormatter.format_r_feedback_voltage_error_msg(config, dps_log)
            return message

    @staticmethod
    def format_fw_upload_error_msg(dps_log: DPSLog) -> str:
        return f"ERROR [{dps_log.x},{dps_log.y}][programování]: {dps_log.fw_upload_message}\n\n"

    @staticmethod
    def format_led_current_error_msg(config: FirmwareConfig, dps_log: DPSLog, mode: int = 1) -> str:
        led_current = dps_log.led_current_mode1 if mode == 1 else dps_log.led_current_mode2
        spec = config.led_current_mode1 if mode == 1 else config.led_current_mode2
        return f"ERROR [{dps_log.x},{dps_log.y}] [testování]: proud LED (mód {mode}) mimo specifikaci {led_current:.0f} mA x ({spec[0]}, {spec[1]}) mA\n\n"

    @staticmethod
    def format_button_led_voltage_error_msg(config: FirmwareConfig, dps_log: DPSLog) -> str:
        return f"ERROR [{dps_log.x},{dps_log.y}] [testování]: napětí LED tlačítka mimo specifikaci {dps_log.button_led_voltage:.0f} mV x ({config.button_led_voltage[0]}, {config.button_led_voltage[1]}) mV\n\n"

    @staticmethod
    def format_r_feedback_voltage_error_msg(config: FirmwareConfig, dps_log: DPSLog) -> str:
        return f"ERROR [{dps_log.x},{dps_log.y}] [testování]: napětí ZV rezistoru mimo specifikaci {dps_log.r_feedback_voltage:.0f} mV x ({config.r_feedback_voltage[0]}, {config.r_feedback_voltage[1]}) mV\n\n"
