"""A python class for the Delcom USBLMP 904x multi-color visual signal indicator.

This has been tested with the 904005-SB but should work with most of the other
indicators.

Requires the Signal 11 HIDAPI and cython-hidapi.

Copyright (c) 2026 Aaron Linville <aaron@linville.org>
"""

import datetime
import enum
from importlib.metadata import PackageNotFoundError, version

import hid

try:
    __version__ = version("delcom904x")
except PackageNotFoundError:
    __version__ = "0+unknown"

VENDOR_ID = 0x0FC5
PRODUCT_ID = 0xB080

# The buzzer tone period is set in 256 µs units (1-255).
BUZZER_MIN_FREQUENCY = 16  # ~1 / (255 * 256 µs)
BUZZER_MAX_FREQUENCY = 3906  # ~1 / (1 * 256 µs)


class Color(enum.IntFlag):
    """LED colors, combinable with ``|``. Yellow is wired the same as blue."""

    GREEN = 1
    RED = 2
    BLUE = 4
    YELLOW = 4  # Alias of BLUE


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

    def __init__(self, *, reset=True):
        """Constructs and attempts to attach to any available Delcom 904x Multi-Color
        Visual Indicator.

        Args:
            reset: Turn off the LEDs and buzzer after attaching. Pass False to
                keep the device's current state, e.g. so a running buzzer is not
                silenced.
        """

        self._device = hid.device()
        self._device.open(VENDOR_ID, PRODUCT_ID)

        if not reset:
            return

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
            for name, mask in (
                ("green", Color.GREEN),
                ("red", Color.RED),
                ("blue_yellow", Color.BLUE),
            )
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

    def set_color(self, colors, *, flashing=False, cycle_time=0):
        """Enables the colors with optional flashing or color cycling."""

        # Use a plain int so ~colors inverts all 8 bits, not just the Color flags.
        colors = int(colors)
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

            for pin, color in enumerate((Color.GREEN, Color.RED, Color.BLUE)):
                if colors & color:
                    self._set_duty_cycle(pin, cycle_time, off_time)
                    self._set_phase_delay(pin, delay)
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

    def enable_buzzer(self, *, frequency=1000, on_ms=200, off_ms=100, repeat=1):
        """Enables the buzzer.

        Args:
            frequency: Tone frequency in Hz (16-3906). The device sets the tone
                period in 256 µs steps, so the frequency is rounded to the nearest
                supported value.
            on_ms: How long each beep lasts, in milliseconds (50-12750). Rounded
                down to a multiple of 50 ms.
            off_ms: Silence between beeps, in milliseconds (0-12750). Rounded down
                to a multiple of 50 ms.
            repeat: Number of beeps (1-255), or 0 to buzz continuously until
                ``disable_buzzer()`` or ``reset()`` is called.

        Raises:
            ValueError: If any argument is out of range.
        """

        if not BUZZER_MIN_FREQUENCY <= frequency <= BUZZER_MAX_FREQUENCY:
            raise ValueError(
                f"frequency must be between {BUZZER_MIN_FREQUENCY} and"
                f" {BUZZER_MAX_FREQUENCY} Hz, got {frequency}"
            )
        if not 50 <= on_ms <= 255 * 50:
            raise ValueError(f"on_ms must be between 50 and 12750, got {on_ms}")
        if not 0 <= off_ms <= 255 * 50:
            raise ValueError(f"off_ms must be between 0 and 12750, got {off_ms}")
        if not 0 <= repeat <= 255:
            raise ValueError(f"repeat must be between 0 and 255, got {repeat}")

        # Tone period in 256 µs units: frequency = 1 / (period * 256 µs)
        period = min(255, max(1, round(1 / (frequency * 256e-6))))

        self._device.write(
            [
                102,
                70,
                0x1,  # Enable Buzzer
                period,  # Frequency (tone period, 256 µs units)
                0x0,
                0x0,
                0x0,
                0x0,
                repeat,  # Repeat count, 0 = continuous
                on_ms // 50,  # Duty cycle (on), 50 ms units
                off_ms // 50,  # Duty cycle (off), 50 ms units
                0x0,
                0x0,
                0x0,
                0x0,
                0x0,
            ]
        )
