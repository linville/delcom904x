# A python class for the Delcom USBLMP 904x multi-color visual signal indicator. This
# has been tested with the 904007-SB but should work with most of the other
# indicators.
#
# Requires the Signal 11 HIDAPI and cython-hidapi.
#
# Copyright (c) 2019 Aaron Linville <aaron@linville.org>

import datetime

import hid

VENDOR_ID = 0x0FC5
PRODUCT_ID = 0xB080

green = 1
red = 2
blue = 4
yellow = 4


def list_devices():
    """Lists all the Delcom USBLMP 904x devices"""
    for d in hid.enumerate(VENDOR_ID, PRODUCT_ID):
        for key in sorted(d.keys()):
            print(f"{key} : {d[key]}")
        print()


class DelcomMultiColorIndicator:
    """A python class for the Delcom USBLMP 904x Multi-color
    Visual Signal Indicators."""

    # Command Packet Format:
    # Byte 0     - Major Command
    # Byte 1     - Minor Command
    # Byte 2     - Data LSB
    # Byte 3     - Data MSB
    # Bytes 4-7  - Data HID
    # Bytes 8-16 - Data External (Optional)

    def __init__(self):
        """Constructs and attempts to attach to any available Delcom 904x Multi-Color
        Visual Indicator."""

        self._device = hid.device()
        self._device.open(VENDOR_ID, PRODUCT_ID)

        try:
            self.reset()
        except Exception:
            self._device.close()
            raise

    def close(self):
        """Close the USB connection gracefully"""
        self._device.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()

    def info(self):
        """Return the USB, firmware and current configuration details
        of the attached multi-color indicator as a dict."""
        usb = {
            "manufacturer": self._device.get_manufacturer_string(),
            "product": self._device.get_product_string(),
            "serial": self._device.get_serial_number_string(),
        }

        fw = self._device.get_feature_report(10, 8)
        firmware = {
            "serial": int.from_bytes(bytes(fw[0:4]), "little"),
            "version": fw[4],
            "date": datetime.date(fw[7] + 2000, fw[6], fw[5]),
        }

        ports = self._device.get_feature_report(100, 4)
        # Color bits are active-low: a cleared bit means the color is enabled.
        enabled_colors = [
            name
            for name, mask in (("green", green), ("red", red), ("blue_yellow", blue))
            if not ports[1] & mask
        ]

        return {
            "usb": usb,
            "firmware": firmware,
            "ports": {
                "port0": ports[0],
                "port1": ports[1],
                "port1_enabled_colors": enabled_colors,
                "port1_clock_enable": ports[2],
                "port2": ports[3],
            },
        }

    def reset(self):
        """Turns off all the LEDs and Buzzers."""

        self.set_color(0)
        self.disable_buzzer()

    def set_color(self, colors, flashing=False, cycle_time=0):
        """Enables the colors with optional flashing or color cycling."""

        self._device.write([101, 12, colors, 0xFF])

        # If flash is not enabled, ensure it's disabled.
        if flashing or cycle_time > 0:
            self._device.write([101, 20, ~colors & 0xFF, colors])
        else:
            self._device.write([101, 20, 0xF, 0x0])

        if cycle_time > 0:
            # Syncronize clock generation
            delay = 0
            off_time = (colors.bit_count() - 1) * cycle_time

            if colors & green:
                # print(f"Cycle green: {cycle_time}, {delay}, {off_time}")
                self._set_duty_cycle(0, cycle_time, off_time)
                self._set_phase_delay(0, delay)
                delay += cycle_time

            if colors & red:
                # print(f"Cycle red: {cycle_time}, {delay}, {off_time}")
                self._set_duty_cycle(1, cycle_time, off_time)
                self._set_phase_delay(1, delay)
                delay += cycle_time

            if colors & blue:
                # print(f"Cycle blue: {cycle_time}, {delay}, {off_time}")
                self._set_duty_cycle(2, cycle_time, off_time)
                self._set_phase_delay(2, delay)
                delay += cycle_time

            # No initial phase delay
            self._device.write([101, 25, colors, 0])  # Selected on pins
        else:
            # All pins
            # No initial phase delay
            self._device.write([101, 25, 0xF, 0])

    def _set_duty_cycle(self, color_pin, on_time, off_time):
        """Internal method to set the duty cycle on a pin, used for color cycling."""

        self._device.write(
            [
                101,
                21 + color_pin,  # Pin to set duty cycle on
                off_time,  # High duty cycle
                on_time,
            ]
        )  # Low duty cycle

    def _set_phase_delay(self, color_pin, delay_time):
        """Internal method to set the initial delay on a pin, used for color cycling."""

        self._device.write(
            [
                101,
                26 + color_pin,  # Pin to delay turning on
                delay_time,
                0x0,
            ]
        )

    def set_intensity(self, intensity, colors):
        """Sets the intensity of a color using pulse-width modulation (0-100 %)."""

        self._device.write([101, 34, colors, intensity])

    def disable_buzzer(self):
        """Disables the buzzer."""

        self._device.write(
            [
                102,
                70,
                0x0,  # Disable Buzzer
                0x0,  # Frequency
                0x0,
                0x0,
                0x0,
                0x0,
                0,
                0,  # Duty cycle (on), 50 ms units
                0,  # Duty cycle (off), 50 ms units
                0x0,
                0x0,
                0x0,
                0x0,
                0x0,
            ]
        )

    def enable_buzzer(self, freq, duty_on, duty_off, repeat):
        """Enables the buzzer with a duty cycle and repetition. Frequency is currently
        hardcoded."""

        self._device.write(
            [
                102,
                70,
                0x1,  # Enable Buzzer
                0x4,  # Frequency
                0x0,
                0x0,
                0x0,
                0x0,
                repeat,
                duty_on // 50,  # Duty cycle (on), 50 ms units
                duty_off // 50,  # Duty cycle (off), 50 ms units
                0x0,
                0x0,
                0x0,
                0x0,
                0x0,
            ]
        )
