#!/usr/bin/env python

# This is an example of how to control the Delcom USBLMP 904x device
#
# Copyright (c) 2025 Aaron Linville <aaron@linville.org>

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
    parser.add_argument("--buzzer", action="store_true", help="Buzzes three times.")
    parser.add_argument("--reset", action="store_true", help="Resets the device.")

    return parser


def main():
    args = setup_argparse().parse_args()

    if args.list:
        delcom904x.list_devices()
        sys.exit()

    color = 0

    if args.green:
        color = color | delcom904x.green

    if args.red:
        color = color | delcom904x.red

    if args.blue or args.yellow:
        color = color | delcom904x.blue

    with delcom904x.DelcomMultiColorIndicator() as light:
        if args.info:
            light.info()

        if args.reset:
            light.reset()
            sys.exit()

        if args.buzzer:
            light.enable_buzzer(0, 200, 100, 3)

        # User didn't specify a color, so just exit
        if not color:
            sys.exit("Exiting, color must be specified.")

        light.set_color(color, flashing=args.flash, cycle_time=args.cycle)

        if args.intensity is not None:
            light.set_intensity(args.intensity, color)


if __name__ == "__main__":
    main()
