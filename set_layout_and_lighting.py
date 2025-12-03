from pywinusb import hid
import struct, time

from device.device import Device
from device.cv09.cv09 import CV09


class HIDDevice:
    def __init__(self, device: Device):
        self.device = device
        self.d = None
        self.out_rep = None
        self.out_len = None

        self._open_iface()

    def _open_iface(self):
        print("Opening interface...")
        devices = hid.HidDeviceFilter(vendor_id=self.device.vid, product_id=self.device.pid).get_devices()
        if not devices:
            raise RuntimeError(f"{self.device.name} not found")
        for device in devices:
            device.open()
            outs = device.find_output_reports()
            if outs and device.hid_caps.output_report_byte_length >= self.device.output_report_byte_length:
                self.d = device
                self.out_rep = outs[0]
                self.out_len = device.hid_caps.output_report_byte_length
                return
            device.close()
        raise RuntimeError(
            f"No suitable Output report (need ≥{self.device.output_report_byte_length} bytes including report_id)"
        )

    def send(self, payload: bytes, delay=0.003):
        data_bytes = self.out_len - 1
        # first byte always report_id, then payload bytes, then zeros
        raw = [self.out_rep.report_id] + list(payload[:data_bytes]) + [0] * (data_bytes - min(len(payload), data_bytes))
        self.out_rep.set_raw_data(raw)
        self.out_rep.send()
        time.sleep(delay)

    def commit(self):
        self.send(bytes([self.device.CMD_COMMIT, 0x03, 0x00, 0x00]))
        time.sleep(1)  # min 0.6 - works


class HIDSetter:
    ADDR_BRIGHTNESS = 1  # 0..255  (8 bit)
    ADDR_EFFECT = 2  # 1..6 effects (8 bit)
    ADDR_EFFECT_SPEED = 3  # 0..255 (8 bit)
    ADDR_COLOR_PACKED = 4  # color (16-bit)

    def __init__(self, device: Device, layout: list[list[str]]):
        self.device: Device = device
        self.layout: list[list[str]] = layout

        self.hid_device = HIDDevice(self.device)

    def start(self):
        try:
            self.set_layout()
            self.turn_off_lighting()
            print("Done")
        finally:
            self.hid_device.d.close()

    def set_layout(self):
        for i, layer in enumerate(self.layout):
            print(f"Writing layer #{i}...")
            self.set_layer(layer_number=i, keys=layer, keycodes=self.device.keycodes())
        # self.hid_device.commit()

    def set_layer(self, layer_number: int, keys: list[str], keycodes: dict[str, bytes]):
        for idx, name in enumerate(keys):
            self.set_key_by_index(layer_number, idx, keycodes.get(name, 0))

    # ToDo: is this works only to CV09? idk
    def set_key_by_index(self, layer: int, index: int, keycode: int):
        # [05, layer, 00, index, key_hi, key_lo]
        payload = struct.pack(
            ">BBBBH",
            self.device.CMD_SET_KEY,
            layer & 0xFF,
            0x00,
            index & 0xFF,
            keycode & 0xFFFF
        )
        self.hid_device.send(payload)

    def set_lighting(self, addr, val):
        # [07, page, addr, val_hi, val_lo];
        page = 0x03
        payload = struct.pack(
            ">BBBH",
            self.device.CMD_SET_LIGHTING,
            page & 0xFF,
            addr & 0xFF,
            val & 0xFFFF,
        )
        self.hid_device.send(payload)

    def turn_off_lighting(self):
        print("Turning off lighting...")
        self.set_lighting(self.ADDR_EFFECT, 0x0000)  # All Off
        self.set_lighting(self.ADDR_BRIGHTNESS, 0x0000)  # Brightness 0
        self.hid_device.commit()

    def set_brightness(self):
        self.set_lighting(self.ADDR_BRIGHTNESS, 0x0000)  # val 0x0000 - 0x00ff
        self.hid_device.commit()

    def set_mode(self):
        self.set_lighting(self.ADDR_EFFECT, 0x0000)  # val 0x0000 - 0x0006

    def set_effect(self):
        self.set_lighting(self.ADDR_EFFECT, 0x0000)  # val 0x0000 - 0x0006

    def set_effect_speed(self):
        self.set_lighting(self.ADDR_EFFECT_SPEED, 0x0000)  # val 0x0000 - 0x00ff

    def set_color(self, r: int, g: int, b: int):
        val = self.rgb_to_hhss(r, g, b)
        self.set_lighting(self.ADDR_COLOR_PACKED, val)  # val 0x0000 - 0xffff

    @staticmethod
    def rgb_to_hhss(r, g, b):
        """
        RGB (0..255 each) -> 16-bit 0xHHSS (Hue byte, Saturation byte), Value assumed = 255.
        No libraries.
        """
        # Clamp
        r = max(0, min(255, int(r)))
        g = max(0, min(255, int(g)))
        b = max(0, min(255, int(b)))

        # Normalize to 0..1
        r1, g1, b1 = r / 255.0, g / 255.0, b / 255.0
        cmax = max(r1, g1, b1)
        cmin = min(r1, g1, b1)
        delta = cmax - cmin

        # Hue in [0,1)
        if delta == 0:
            h = 0.0
        elif cmax == r1:
            h = ((g1 - b1) / delta) % 6.0
        elif cmax == g1:
            h = (b1 - r1) / delta + 2.0
        else:  # cmax == b1
            h = (r1 - g1) / delta + 4.0
        h = (h / 6.0) % 1.0  # normalize

        # Saturation in [0,1]
        s = 0.0 if cmax == 0 else (delta / cmax)

        # Map to bytes
        H = int(round(h * 255)) % 256  # wrap 1.0 -> 0
        S = int(round(s * 255))
        return (H << 8) | S


def main():
    device = CV09
    layout = [
        [
            "KC_PSCR", "KC_F13", "KC_CALC",
            "KC_F15", "KC_F17", "KC_F18",
            "KC_F14", "KC_F16", "CUSTOM_FN(1)"
        ],
        [
            "KC_VOLU", "KC_NO", "KC_NO",
            "KC_VOLD", "KC_NO", "KC_NO",
            "KC_MPLY", "KC_NO", "CUSTOM_FN(0)"
        ]
    ]

    hid_setter = HIDSetter(device, layout)
    hid_setter.start()


if __name__ == "__main__":
    main()
