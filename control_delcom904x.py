#!/usr/bin/python -B

# This is an example of how to control the Delcom USBLMP 904x device
#
# Copyright (c) 2015 Aaron Linville <aaron@linville.org>

import argparse
import delcom904x

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Convert and generate Chmaber Director log files.")
    parser.add_argument('--list', action='store_true', help = "List all USB devices.")
    parser.add_argument('--info', action='store_true', help = "Returns info on the device.")
    parser.add_argument('--red', action='store_true', help = "Enable the red light.")
    parser.add_argument('--green', action='store_true', help = "Enable the green light.")
    parser.add_argument('--blue', action='store_true', help = "Enable the blue light.")
    parser.add_argument('--flash', action='store_true', help = "Turns on flashing.")
    parser.add_argument('--cycle', nargs = '?', metavar = '100', const = 100, type=int, help = "Turns on cycling.")
    parser.add_argument('--intensity', nargs = '?', metavar = '80', const = 80, type=int, help = "Sets brightness: 0-100.")
    parser.add_argument('--buzzer', action='store_true', help = "Buzzes three times.")
    parser.add_argument('--reset', action='store_true', help = "Resets the device.")
    
    args = parser.parse_args()

    if(args.list):
        delcom904x.list()
        
    color = 0
        
    if(args.green):
        color = color | delcom904x.green
    
    if(args.red):
        color = color | delcom904x.red
    
    if(args.blue):
        color = color | delcom904x.blue
    
    light = delcom904x.DelcomMultiColorIndicator()
    
    if(args.reset):
        light.reset()
        exit()
    
    light.set_color(color, flashing = args.flash, cycle_time = args.cycle)
        
    if(args.intensity):
        light.set_intensity(args.intensity, color)
    
    if(args.buzzer):
        light.enable_buzzer(0, 200, 100, 3)
    
    if(args.info):
        light.info()
