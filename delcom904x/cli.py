#!/usr/bin/env python
"""An example of how to control the Delcom USBLMP 904x device.

Copyright (c) 2026 Aaron Linville <aaron@linville.org>
"""

import argparse
import sys

import delcom904x


def _int_range(min_val, max_val):
    """Helper used to validate CLI argument ranges."""

    def validator(value):
        try:
            val = int(value)
        except ValueError as err:
            raise argparse.ArgumentTypeError(
                f"'{value}' is not a valid integer"
            ) from err

        if val < min_val or val > max_val:
            raise argparse.ArgumentTypeError(
                f"Value {val} is out of range. Must be between {min_val} and"
                f" {max_val}."
            )
        return val

    return validator


def setup_argparse():
    parser = argparse.ArgumentParser(
        description="Control the Delcom USBLMP 904x visual signal indicator."
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {delcom904x.__version__}",
    )
    parser.add_argument("--list", action="store_true", help="List all USB devices.")
    parser.add_argument(
        "--info", action="store_true", help="Returns info on the device."
    )
    parser.add_argument("--red", action="store_true", help="Enable the red light.")
    parser.add_argument("--green", action="store_true", help="Enable the green light.")
    parser.add_argument("--blue", action="store_true", help="Enable the blue light.")
    parser.add_argument(
        "--yellow",
        action="store_true",
        help="Enable the yellow light (if equipped; synonym for blue).",
    )
    parser.add_argument("--flash", action="store_true", help="Turns on flashing.")
    parser.add_argument(
        "--cycle",
        nargs="?",
        metavar="100",
        const=100,
        default=0,
        type=_int_range(0, 100),
        help="Turns on cycling.",
    )
    parser.add_argument(
        "--intensity",
        nargs="?",
        metavar="80",
        const=80,
        type=_int_range(0, 100),
        help="Sets brightness: 0-100.",
    )
    buzzer = parser.add_argument_group("buzzer options")
    buzzer.add_argument(
        "--buzz",
        nargs="?",
        metavar="3",
        const=3,
        type=_int_range(1, 255),
        help="Buzz N times: 1-255.",
    )
    buzzer.add_argument(
        "--buzz-freq",
        metavar="1000",
        default=1000,
        type=_int_range(
            delcom904x.BUZZER_MIN_FREQUENCY, delcom904x.BUZZER_MAX_FREQUENCY
        ),
        help=(
            f"Buzzer frequency in Hz: {delcom904x.BUZZER_MIN_FREQUENCY}-"
            f"{delcom904x.BUZZER_MAX_FREQUENCY}."
        ),
    )
    buzzer.add_argument(
        "--silence", action="store_true", help="Stop the buzzer, leaving the LEDs."
    )
    parser.add_argument("--reset", action="store_true", help="Resets the device.")

    return parser


def main():
    args = setup_argparse().parse_args()

    if args.list:
        delcom904x.list_devices()
        sys.exit()

    color = delcom904x.Color(0)

    if args.green:
        color |= delcom904x.Color.GREEN

    if args.red:
        color |= delcom904x.Color.RED

    if args.blue or args.yellow:
        color |= delcom904x.Color.BLUE

    if not (args.info or args.reset or args.buzz or args.silence or color):
        sys.exit("Exiting, a color or buzzer option must be specified.")

    # Don't reset on attach, so a buzzer started by an earlier run keeps going.
    with delcom904x.DelcomMultiColorIndicator(reset=False) as light:
        if args.info:
            import pprint

            pprint.pprint(light.info(), sort_dicts=False)

        if args.reset:
            light.reset()
            sys.exit()

        if args.silence:
            light.disable_buzzer()

        if args.buzz:
            light.enable_buzzer(frequency=args.buzz_freq, repeat=args.buzz)

        if color:
            light.set_color(color, flashing=args.flash, cycle_time=args.cycle)

            if args.intensity is not None:
                light.set_intensity(args.intensity, color)


if __name__ == "__main__":
    main()
