from device.cv09.device import CV09
from hid_setter import HIDSetter


def main():
    device = CV09

    # we can provide str - keys from keycodes.json
    # and int - raw bytes
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
