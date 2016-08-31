#!/usr/bin/env python3
import serial
import sys
import argparse
import re
import os
import picker

if os.geteuid() != 0:
    sys.exit("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'.")

parser = argparse.ArgumentParser(description="Change NZXT Hue+ LEDs")
parser.add_argument("-p", "--port", default="/dev/ttyACM0", type=str, help="The port, defaults to /dev/ttyACM0")
parser.add_argument("-c", "--channel", type=int, default=1, help="The channel, defaults to 1")
parser.add_argument("-g", "--gui", type=int, default=0, help="How many colors of GUI picker")
subparsers = parser.add_subparsers(help="The type of color (fixed, breathing)", dest='command')

parser_fixed = subparsers.add_parser('fixed', help="One single fixed color")
parser_fixed.add_argument("color", type=str, help="Color in hex")

parser_breathing = subparsers.add_parser('breathing', help="Breathing through a set of colors")
parser_breathing.add_argument("speed", type=int, help="Speed from 0(Slowest) to 4(Fastest)")
parser_breathing.add_argument("colors", type=str, nargs='+', help="Color(s) in hex")

parser_fading = subparsers.add_parser('fading', help="Fading through a set of colors")
parser_fading.add_argument("speed", type=int, help="Speed from 0(Slowest) to 4(Fastest)")
parser_fading.add_argument("colors", type=str, nargs='+', help="Color(s) in hex")

parser_marquee = subparsers.add_parser('marquee', help="A strip of color running")
parser_marquee.add_argument("speed", type=int, help="Speed from 0(Slowest) to 4(Fastest)")
parser_marquee.add_argument("-c", "--comet", action="store_true", help="Enable comet mode (leave a trail)")
parser_marquee.add_argument("-b", "--backwards", action="store_true", help="Enable going backwards")
parser_marquee.add_argument("size", type=int, help="The size of the group of runners (0=2, 1=3, 2=5, 3=10)")
parser_marquee.add_argument("colors", type=str, nargs=2, help="Foreground and background colors in hex")

parser_cover_marquee = subparsers.add_parser('cover_marquee', help="A strip of color running (multiple colors)")
parser_cover_marquee.add_argument("speed", type=int, help="Speed from 0(Slowest) to 4(Fastest)")
parser_cover_marquee.add_argument("-b", "--backwards", action="store_true", help="Enable going backwards")
parser_cover_marquee.add_argument("colors", type=str, nargs='+', help="Colors in hex")

parser_pulse = subparsers.add_parser('pulse', help="Pulsing through a set of colors")
parser_pulse.add_argument("speed", type=int, help="Speed from 0(Slowest) to 4(Fastest)")
parser_pulse.add_argument("colors", type=str, nargs='+', help="Color(s) in hex")

parser_spectrum = subparsers.add_parser('spectrum', help="Pulsing through a set of colors")
parser_spectrum.add_argument("speed", type=int, help="Speed from 0(Slowest) to 4(Fastest)")
parser_spectrum.add_argument("-b", "--backwards", action="store_true", help="Enable going backwards")

parser_alternating = subparsers.add_parser('alternating', help="Two alternating colors")
parser_alternating.add_argument("speed", type=int, help="Speed from 0(Slowest) to 4(Fastest)")
parser_alternating.add_argument("-m", "--moving", action="store_true", help="Enable movement")
parser_alternating.add_argument("-b", "--backwards", action="store_true", help="Enable going backwards (requires movement)")
parser_alternating.add_argument("size", type=int, help="The size of the group of runners (0=2, 1=3, 2=5, 3=10)")
parser_alternating.add_argument("colors", type=str, nargs=2, help="First and second colors in hex")

parser_candlelight = subparsers.add_parser('candlelight', help="A flickering color")
parser_candlelight.add_argument("color", type=str, help="Color in hex")

parser_power = subparsers.add_parser('power', help="Control power to the channels")
parser_power.add_argument("state", type=str, help="State (on/off)")

args = parser.parse_args()

ser = serial.Serial(args.port, 256000)
initial = [bytearray([70, 0, 192, 0, 0, 0, 255]), bytearray([75, 2, 192, 0, 0, 0, 0])]

def fixed(ser, gui, channel, color):
    global initial
    for array in initial:
        ser.write(array)
        out = ser.read()
        pass

    if gui != 0:
        color = picker.pick("Color")

    ser.write(bytearray.fromhex("4B0"+str(channel)+"C0"+color+"00"))
    out = ser.read()
    print("DONE!")

def breathing(ser, gui, channel, color, speed):
    global initial
    for array in initial:
        ser.write(array)
        out = ser.read()
        pass

    if 1 <= gui <= 8:
        color = []
        for i in range(gui):
            color.append(picker.pick("Color "+str(i+1)+ " of "+str(gui)))

    ser.write(bytearray.fromhex("4B0"+str(channel)+"CA"+color[0]+"0"+str(speed)))
    out = ser.read()
    last_byte = speed
    for other_color in color[1:]:
        last_byte = last_byte+20
        ser.write(bytearray.fromhex("4B0"+str(channel)+"CA"+other_color+str(last_byte)))
        out = ser.read()

    print("DONE!")

def fading(ser, gui, channel, color, speed):
    global initial
    for array in initial:
        ser.write(array)
        out = ser.read()
        pass

    if 1 <= gui <= 8:
        color = []
        for i in range(gui):
            color.append(picker.pick("Color "+str(i+1)+ " of "+str(gui)))

    ser.write(bytearray.fromhex("4B0"+str(channel)+"C1"+color[0]+"0"+str(speed)))
    out = ser.read()
    last_byte = speed
    for other_color in color[1:]:
        last_byte = last_byte+20
        ser.write(bytearray.fromhex("4B0"+str(channel)+"C1"+other_color+str(last_byte)))
        out = ser.read()

    print("DONE!")

def marquee(ser, gui, channel, color, speed, size, comet, direction):
    global initial
    for array in initial:
        ser.write(array)
        out = ser.read()
        pass

    if gui != 0:
        color = []
        gui = 2
        for i in range(2):
            color.append(picker.pick("Color "+str(i+1)+ " of "+str(gui)))

    if comet:
        option = size * 8 + speed | 128
    else:
        option = size * 8 + speed | 0

    if direction:
        first_option = format(option, '02x')
        ser.write(bytearray.fromhex("4B0"+str(channel)+"C5"+color[0]+first_option))
        out = ser.read()
        second_option = format(option+32, '02x')
        ser.write(bytearray.fromhex("4B0"+str(channel)+"C5"+color[1]+second_option))
        out = ser.read()
    else:
        first_option = format(option, '02x')
        ser.write(bytearray.fromhex("4B0"+str(channel)+"C4"+color[0]+first_option))
        out = ser.read()
        second_option = format(option+32, '02x')
        ser.write(bytearray.fromhex("4B0"+str(channel)+"C4"+color[1]+second_option))
        out = ser.read()

    print("DONE!")

def cover_marquee(ser, gui, channel, color, speed, direction):
    global initial
    for array in initial:
        ser.write(array)
        out = ser.read()
        pass

    if 1 <= gui <= 8:
        color = []
        for i in range(gui):
            color.append(picker.pick("Color "+str(i+1)+ " of "+str(gui)))

    option = speed | 0

    if direction:
        first_option = format(option, '02x')
        ser.write(bytearray.fromhex("4B0"+str(channel)+"C7"+color[0]+first_option))
        out = ser.read()

        last_byte = option
        for other_color in color[1:]:
            last_byte = last_byte+32
            loop_option = format(last_byte, '02x')
            ser.write(bytearray.fromhex("4B0"+str(channel)+"C7"+other_color+loop_option))
            out = ser.read()
    else:
        first_option = format(option, '02x')
        ser.write(bytearray.fromhex("4B0"+str(channel)+"C6"+color[0]+first_option))
        out = ser.read()

        last_byte = option
        for other_color in color[1:]:
            last_byte = last_byte+32
            loop_option = format(last_byte, '02x')
            ser.write(bytearray.fromhex("4B0"+str(channel)+"C6"+other_color+loop_option))
            out = ser.read()

    print("DONE!")

def pulse(ser, gui, channel, color, speed):
    global initial
    for array in initial:
        ser.write(array)
        out = ser.read()
        pass

    if 1 <= gui <= 8:
        color = []
        for i in range(gui):
            color.append(picker.pick("Color "+str(i+1)+ " of "+str(gui)))

    ser.write(bytearray.fromhex("4B0"+str(channel)+"C9"+color[0]+"0"+str(speed)))
    out = ser.read()
    last_byte = speed
    for other_color in color[1:]:
        last_byte = last_byte+20
        ser.write(bytearray.fromhex("4B0"+str(channel)+"C9"+other_color+str(last_byte)))
        out = ser.read()

    print("DONE!")

def spectrum(ser, channel, speed, direction):
    global initial
    for array in initial:
        ser.write(array)
        out = ser.read()
        pass

    if direction:
        ser.write(bytearray.fromhex("4B0"+str(channel)+"C30000FF0"+str(speed)))
    else:
        ser.write(bytearray.fromhex("4B0"+str(channel)+"C20000FF0"+str(speed)))
    out = ser.read()

def alternating(ser, gui, channel, color, speed, size, moving, direction):
    global initial
    for array in initial:
        ser.write(array)
        out = ser.read()
        pass

    if gui != 0:
        color = []
        gui = 2
        for i in range(2):
            color.append(picker.pick("Color "+str(i+1)+ " of "+str(gui)))

    if moving:
        if direction:
            option = size * 8 + speed | 192
        else:
            option = size * 8 + speed | 128
    else:
        option = size * 8 + speed

    ser.write(bytearray.fromhex("4B0"+str(channel)+"C8"+color[0]+format(option, '02x')))
    out = ser.read()
    ser.write(bytearray.fromhex("4B0"+str(channel)+"C8"+color[1]+format(option+32, '02x')))
    out = ser.read()

def candlelight(ser, gui, channel, color):
    global initial
    for array in initial:
        ser.write(array)
        out = ser.read()
        pass

    if gui != 0:
        color = picker.pick("Color")

    ser.write(bytearray.fromhex("4B0"+str(channel)+"CC"+color+"00"))
    out = ser.read()

def power(ser, channel, state):
    if state.lower() == 'on':
        fixed(ser, 0, channel, "FFFFFF")
    elif state.lower() == 'off':
        fixed(ser, 0, channel, "000000")
    else:
        print("INVALID STATE!")
        sys.exit(-1)

if args.command == "fixed":
    fixed(ser, args.gui, args.channel, args.color)
elif args.command == 'breathing':
    breathing(ser, args.gui, args.channel, args.colors, args.speed)
elif args.command == 'fading':
    fading(ser, args.gui, args.channel, args.colors, args.speed)
elif args.command == 'marquee':
    marquee(ser, args.gui, args.channel, args.colors, args.speed, args.size, args.comet, args.backwards)
elif args.command == 'cover_marquee':
    cover_marquee(ser, args.gui, args.channel, args.colors, args.speed, args.backwards)
elif args.command == 'pulse':
    pulse(ser, args.gui, args.channel, args.colors, args.speed)
elif args.command == 'spectrum':
    spectrum(ser, args.channel, args.speed, args.backwards)
elif args.command == 'alternating':
    alternating(ser, args.gui, args.channel, args.colors, args.speed, args.size, args.moving, args.backwards)
elif args.command == 'candlelight':
    candlelight(ser, args.gui, args.channel, args.color)
elif args.command == 'power':
    power(ser, args.channel, args.state)
else:
    print("INVALID COMMAND")
    sys.exit(-1)
