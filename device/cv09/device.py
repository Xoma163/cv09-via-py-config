from pathlib import Path

from device.device import Device


class CV09(Device):
    vid = 0xD747
    pid = 0x0009
    name = "CV09"
    via_version = 12
    output_report_byte_length = 33
    keycodes_file = Path('device/cv09/cv09_keycodes.json') # v12 + custom cv09 keycodes

    CMD_SET_KEY = 0x05  # [05, layer, 00, index, 00, key_lo, key_hi]
    CMD_SET_LIGHTING = 0x07  # [07, page, addr, val_lo, val_hi]
    CMD_COMMIT = 0x09  # [09, 03, 00, 00]

