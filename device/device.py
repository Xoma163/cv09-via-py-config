import dataclasses
import json
from pathlib import Path


@dataclasses.dataclass
class Device:
    vid: int
    pid: int
    name: str
    via_version: int
    output_report_byte_length: int
    keycodes_file: Path

    CMD_SET_KEY: int
    CMD_SET_LIGHTING: int
    CMD_COMMIT: int

    @classmethod
    def keycodes(cls) -> dict[str, bytes]:
        with open(cls.keycodes_file) as f:
            data = json.load(f)
        for k, v in data.items():
            data[k] = int(v, 16)
        return data
