from pywinusb import hid
import time

from device.cv09.cv09 import CV09
from device.device import Device

light_mode_translator = {
    1: "brightness",
    2: "mode",
    3: "effect speed",
    4: "color",
}
# CV09 only
command_mode_translator = {
    5: 'set_key',
    7: 'set_light',
    9: 'commit'
}

# ToDo: all of this is unreadable shit

def handler_factory(d):
    path = d.device_path
    in_len = d.hid_caps.input_report_byte_length
    out_len = d.hid_caps.output_report_byte_length

    def on_raw(data):
        b = bytes(data)
        # print(f"\n[RX] path={path}\n     in_len={in_len} out_len={out_len}\n     bytes={b.hex(' ')}")
        print(f"raw = {b.hex(' ')}")

        command = b[1]
        command_mode = command_mode_translator[command]
        if command == 5:
            layer = b[3]
            key_number = b[4]
            key_code = b[5:7].hex()
            print(f"command_mode = {command_mode}, layer = {layer}, key_number = {key_number}, key_code = {key_code}")
        elif command == 7:
            what_to_set_int = b[3]
            light_mode = light_mode_translator[what_to_set_int]
            value = b[4:6].hex()
            print(f"command_mode = {command_mode}, what_to_set = {light_mode}, value = {value}")
        elif command == 9:
            print(f"command_mode = {command_mode}")
        else:
            print(f"something interesting")
        return None

    return on_raw


def listen_devices(device: Device):
    devs = hid.HidDeviceFilter(vendor_id=device.vid, product_id=device.pid).get_devices()
    if not devs:
        print(f"{device.name} not found")
        return
    opened = []
    try:
        print(
            "I've opened the interfaces and am listening for incoming reports.\n"
            "Now switch to VIA and change one key\n"
        )
        for d in devs:
            d.open()
            d.set_raw_data_handler(handler_factory(d))
            print(
                f"- listening: {d.device_path}  (in={d.hid_caps.input_report_byte_length}, out={d.hid_caps.output_report_byte_length})")
            opened.append(d)

        while True:
            time.sleep(1)
    finally:
        for d in opened:
            d.set_raw_data_handler(None)
            d.close()


def main():
    device = CV09
    listen_devices(device)


if __name__ == "__main__":
    main()
