# A python class for the Delcom USBLMP 904x multi-color visual signal indicator. This
# has been tested with the 904007-SB but should work with most of the other
# indicators.
#
# Requires the Signal 11 HIDAPI and cython-hidapi.
#
# Copyright (c) 2019 Aaron Linville <aaron@linville.org>

import hid

vendor_id = 0x0FC5
product_id = 0xB080

green = 1
red = 2
blue = 4


def list():
    """Lists all the Delcom USBLMP 904x devices"""
    for d in hid.enumerate(vendor_id, product_id):
        for key in sorted(d.keys()):
            print(f"{key} : {d[key]}")
        print()


class DelcomMultiColorIndicator:
    """A python class for the Delcom USBLMP 904x Multi-color Visual Signal Indicators."""

    # Command Packet Format:
    # Byte 0     - Major Command
    # Byte 1     - Minor Command
    # Byte 2     - Data LSB
    # Byte 3     - Data MSB
    # Bytes 4-8  - Data HID
    # Bytes 8-16 - Data External (Optional)

    def __init__(self):
        """Constructs and attempts to attach to any available Delcom 904x Multi-Color
        Visual Indicator."""

        try:
            self.h = hid.device()
            self.h.open(vendor_id, product_id)  # Vendor Id, Product Id
            self.reset()
        except OSError as e:
            print(f"Failed: {e}")
            raise

    def info(self):
        """Prints out all the USB, firmware and current configuration
        on the attached multi-color indicator."""

        print(f"USB Manufacturer Id: {self.h.get_manufacturer_string()}")
        print(f"USB Product Id: {self.h.get_product_string()}")
        print(f"USB Serial Id: {self.h.get_serial_number_string()}")

        data = self.h.get_feature_report(10, 8)
        print("Serial: %s" % (data[3] << 32 | data[2] << 16 | data[1] << 8 | data[0]))
        print(f"Firmware version: {data[5]}")
        print(f"Firmware date: {data[7] + 2000}, {data[6]}, {data[5]}")

        data = self.h.get_feature_report(100, 4)
        print("Port 0:", data[0])
        print("Port 1:", data[1])

        str = []
        if ~data[1] & green:
            str.append("Green")
        if ~data[1] & red:
            str.append("Red")
        if ~data[1] & blue:
            str.append("Blue/Yellow")
        if data[1] == 255:
            str.append("None")

        print(f"  Enabled colors: {','.join(str)}")

        print("Port 1 Clock Enable Status:", data[2])
        print("Port 2:", data[3])

    def reset(self):
        """Turns off all the LEDs and Buzzers."""

        self.set_color(0)
        self.disable_buzzer()

    def set_color(self, colors, flashing=False, cycle_time=0):
        """Enables the colors with optional flashing or color cycling."""

        self.h.write([101, 12, colors, 0xFF])

        # If flash is not enabled, ensure it's disabled.
        if flashing or cycle_time > 0:
            self.h.write([101, 20, ~colors & 0xFF, colors])
        else:
            self.h.write([101, 20, 0xF, 0x0])

        if cycle_time > 0:
            # Syncronize clock generation
            delay = 0
            off_time = bin(colors).count("1") * cycle_time - cycle_time

            if colors & green:
                # print(f"Cycle green: {cycle_time}, {delay}, {off_time}")
                self.__set_duty_cycle(0, cycle_time, off_time)
                self.__set_phase_delay(0, delay)
                delay += cycle_time

            if colors & red:
                # print(f"Cycle red: {cycle_time}, {delay}, {off_time}")
                self.__set_duty_cycle(1, cycle_time, off_time)
                self.__set_phase_delay(1, delay)
                delay += cycle_time

            if colors & blue:
                # print(f"Cycle blue: {cycle_time}, {delay}, {off_time}")
                self.__set_duty_cycle(2, cycle_time, off_time)
                self.__set_phase_delay(2, delay)
                delay += cycle_time

            self.h.write(
                [101, 25, colors, 0]  # Selected on pins
            )  # No initial phase delay
        else:
            self.h.write([101, 25, 0xF, 0])  # All pins  # No initial phase delay

    def __set_duty_cycle(self, color_pin, on_time, off_time):
        """Internal method to set the duty cycle on a pin, used for color cycling."""

        self.h.write(
            [
                101,
                21 + color_pin,  # Pin to set duty cycle on
                off_time,  # High duty cycle
                on_time,
            ]
        )  # Low duty cycle

    def __set_phase_delay(self, color_pin, delay_time):
        """Internal method to set the initial delay on a pin, used for color cycling."""

        self.h.write(
            [
                101,
                26 + color_pin,  # Pin to delay turning on
                delay_time,  # High duty cycle
                0x0,
            ]
        )

    def set_intensity(self, intensity, colors):
        """Sets the intensity of a color using pulse-width modulation (0-100 %)."""

        self.h.write([101, 34, colors, intensity])

    def disable_buzzer(self):
        """Disables the buzzer."""

        self.h.write(
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

        self.h.write(
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
                int(duty_on / 50),  # Duty cycle (on), 50 ms units
                int(duty_off / 50),  # Duty cycle (off), 50 ms units
                0x0,
                0x0,
                0x0,
                0x0,
                0x0,
            ]
        )
