from pywinusb import hid
import time

from device.cv09.device import CV09
from device.device import Device

# ToDo: all of this is unreadable shit and works only with cv09

# CV09 only
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


def handler_factory(hid_device, device):
    # path = hid_device.device_path
    # in_len = hid_device.hid_caps.input_report_byte_length
    # out_len = hid_device.hid_caps.output_report_byte_length

    def on_raw(data):
        b = bytes(data)
        # print(
        #     f"\n"
        #     f"[RX] path={path}"
        #     f"\nin_len={in_len} out_len={out_len}"
        #     f"\nbytes={b.hex(' ')}"
        # )
        print(f"raw = {b[:8].hex(' ')}") # print only first 8 bytes
        # print(f"raw = {b.hex(' ')}") # print all
        try:
            command = b[1]
            command_mode = command_mode_translator[command]
            if command == device.CMD_SET_KEY:
                layer = b[3]
                key_number = b[4]
                key_code = b[5:7].hex()
                print(
                    f"command_mode = {command_mode}, layer = {layer}, key_number = {key_number}, key_code = {key_code}")
            elif command == device.CMD_SET_LIGHTING:
                what_to_set_int = b[3]
                light_mode = light_mode_translator[what_to_set_int]
                value = b[4:6].hex()
                print(f"command_mode = {command_mode}, mode = {light_mode}, value = {value}")
            elif command == device.CMD_COMMIT:
                print(f"command_mode = {command_mode}")
            else:
                print(f"something interesting")
            return None
        except Exception:
            print("Cant parse your device, check raw data")

    return on_raw


def listen_devices(device: Device):
    hid_devices = hid.HidDeviceFilter(vendor_id=device.vid, product_id=device.pid).get_devices()
    if not hid_devices:
        print(f"{device.name} not found")
        return
    opened = []
    try:
        print(
            "I've opened the interfaces and am listening for incoming reports.\n"
            "Now switch to VIA and change one key\n"
        )
        for hid_device in hid_devices:
            hid_device.open()
            hid_device.set_raw_data_handler(handler_factory(hid_device, device))
            print(
                f"- listening: {hid_device.device_path}  (in={hid_device.hid_caps.input_report_byte_length}, out={hid_device.hid_caps.output_report_byte_length})")
            opened.append(hid_device)

        while True:
            time.sleep(1)
    finally:
        for hid_device in opened:
            hid_device.set_raw_data_handler(None)
            hid_device.close()


def main():
    device = CV09
    listen_devices(device)


if __name__ == "__main__":
    main()
