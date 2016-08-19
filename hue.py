import serial
import sys
import argparse
import re

parser = argparse.ArgumentParser(description="Change NZXT Hue+ LEDs")
parser.add_argument("port", metavar="PORT", type=str, help="The port")
subparsers = parser.add_subparsers(help="The type of color (fixed, breathing)", dest='command')

parser_fixed = subparsers.add_parser('fixed', help="One single fixed color")
parser_fixed.add_argument("color", type=str, help="Color in hex")

parser_breathing = subparsers.add_parser('breathing', help="Breathing through a set of colors")
parser_breathing.add_argument("speed", type=int, help="Speed from 0(Slowest) to 4(Fastest)")
parser_breathing.add_argument("colors", type=str, nargs='+', help="Color(s) in hex")

parser_breathing = subparsers.add_parser('fading', help="Fading through a set of colors")
parser_breathing.add_argument("speed", type=int, help="Speed from 0(Slowest) to 4(Fastest)")
parser_breathing.add_argument("colors", type=str, nargs='+', help="Color(s) in hex")

parser_breathing = subparsers.add_parser('marquee', help="A strip of color running")
parser_breathing.add_argument("speed", type=int, help="Speed from 0(Slowest) to 4(Fastest)")
parser_breathing.add_argument("-c", "--comet", action="store_true", help="Enable comet mode (leave a trail)")
parser_breathing.add_argument("-b", "--backwards", action="store_true", help="Enable going backwards")
parser_breathing.add_argument("size", type=int, help="The size of the group of runners (0=2, 1=3, 2=5, 3=10)")
parser_breathing.add_argument("colors", type=str, nargs=2, help="Foreground and background colors in hex")

parser_breathing = subparsers.add_parser('cover_marquee', help="A strip of color running (multiple colors)")
parser_breathing.add_argument("speed", type=int, help="Speed from 0(Slowest) to 4(Fastest)")
parser_breathing.add_argument("-b", "--backwards", action="store_true", help="Enable going backwards")
parser_breathing.add_argument("colors", type=str, nargs='+', help="Colors in hex")

parser_breathing = subparsers.add_parser('pulse', help="Pulsing through a set of colors")
parser_breathing.add_argument("speed", type=int, help="Speed from 0(Slowest) to 4(Fastest)")
parser_breathing.add_argument("colors", type=str, nargs='+', help="Color(s) in hex")

parser_breathing = subparsers.add_parser('spectrum', help="Pulsing through a set of colors")
parser_breathing.add_argument("speed", type=int, help="Speed from 0(Slowest) to 4(Fastest)")
parser_breathing.add_argument("-b", "--backwards", action="store_true", help="Enable going backwards")

parser_breathing = subparsers.add_parser('alternating', help="Two alternating colors")
parser_breathing.add_argument("speed", type=int, help="Speed from 0(Slowest) to 4(Fastest)")
parser_breathing.add_argument("-m", "--moving", action="store_true", help="Enable movement")
parser_breathing.add_argument("-b", "--backwards", action="store_true", help="Enable going backwards (requires movement)")
parser_breathing.add_argument("size", type=int, help="The size of the group of runners (0=2, 1=3, 2=5, 3=10)")
parser_breathing.add_argument("colors", type=str, nargs=2, help="First and second colors in hex")

parser_fixed = subparsers.add_parser('candlelight', help="A flickering color")
parser_fixed.add_argument("color", type=str, help="Color in hex")

args = parser.parse_args()

ser = serial.Serial(args.port, 256000)
initial = [bytearray([70, 0, 192, 0, 0, 0, 255]), bytearray([75, 2, 192, 0, 0, 0, 0])]

def fixed(ser, color):
    global initial
    for array in initial:
        ser.write(array)
        out = ser.read()
        pass

    ser.write(bytearray.fromhex("4B01C0"+color+"00"))
    out = ser.read()
    print("DONE!")

def breathing(ser, color, speed):
    global initial
    for array in initial:
        ser.write(array)
        out = ser.read()
        pass

    ser.write(bytearray.fromhex("4B01CA"+color[0]+"0"+str(speed)))
    out = ser.read()
    last_byte = speed
    for other_color in color[1:]:
        last_byte = last_byte+20
        ser.write(bytearray.fromhex("4B01CA"+other_color+str(last_byte)))
        out = ser.read()

    print("DONE!")

def fading(ser, color, speed):
    global initial
    for array in initial:
        ser.write(array)
        out = ser.read()
        pass

    ser.write(bytearray.fromhex("4B01C1"+color[0]+"0"+str(speed)))
    out = ser.read()
    last_byte = speed
    for other_color in color[1:]:
        last_byte = last_byte+20
        ser.write(bytearray.fromhex("4B01C1"+other_color+str(last_byte)))
        out = ser.read()

    print("DONE!")

def marquee(ser, color, speed, size, comet, direction):
    global initial
    for array in initial:
        ser.write(array)
        out = ser.read()
        pass

    if comet:
        option = size * 8 + speed | 128
    else:
        option = size * 8 + speed | 0

    if direction:
        first_option = format(option, '02x')
        ser.write(bytearray.fromhex("4B01C5"+color[0]+first_option))
        out = ser.read()
        second_option = format(option+32, '02x')
        ser.write(bytearray.fromhex("4B01C5"+color[1]+second_option))
        out = ser.read()
    else:
        first_option = format(option, '02x')
        ser.write(bytearray.fromhex("4B01C4"+color[0]+first_option))
        out = ser.read()
        second_option = format(option+32, '02x')
        ser.write(bytearray.fromhex("4B01C4"+color[1]+second_option))
        out = ser.read()

    print("DONE!")

def cover_marquee(ser, color, speed, direction):
    global initial
    for array in initial:
        ser.write(array)
        out = ser.read()
        pass

    option = speed | 0

    if direction:
        first_option = format(option, '02x')
        ser.write(bytearray.fromhex("4B01C7"+color[0]+first_option))
        out = ser.read()

        last_byte = option
        for other_color in color[1:]:
            last_byte = last_byte+32
            loop_option = format(last_byte, '02x')
            ser.write(bytearray.fromhex("4B01C7"+other_color+loop_option))
            out = ser.read()
    else:
        first_option = format(option, '02x')
        ser.write(bytearray.fromhex("4B01C6"+color[0]+first_option))
        out = ser.read()

        last_byte = option
        for other_color in color[1:]:
            last_byte = last_byte+32
            loop_option = format(last_byte, '02x')
            ser.write(bytearray.fromhex("4B01C6"+other_color+loop_option))
            out = ser.read()

    print("DONE!")

def pulse(ser, color, speed):
    global initial
    for array in initial:
        ser.write(array)
        out = ser.read()
        pass

    ser.write(bytearray.fromhex("4B01C9"+color[0]+"0"+str(speed)))
    out = ser.read()
    last_byte = speed
    for other_color in color[1:]:
        last_byte = last_byte+20
        ser.write(bytearray.fromhex("4B01C9"+other_color+str(last_byte)))
        out = ser.read()

    print("DONE!")

def spectrum(ser, speed, direction):
    global initial
    for array in initial:
        ser.write(array)
        out = ser.read()
        pass

    if direction:
        ser.write(bytearray.fromhex("4B01C30000FF0"+str(speed)))
    else:
        ser.write(bytearray.fromhex("4B01C20000FF0"+str(speed)))
    out = ser.read()

def alternating(ser, color, speed, size, moving, direction):
    global initial
    for array in initial:
        ser.write(array)
        out = ser.read()
        pass

    if moving:
        if direction:
            option = size * 8 + speed | 192
        else:
            option = size * 8 + speed | 128
    else:
        option = size * 8 + speed

    ser.write(bytearray.fromhex("4B01C8"+color[0]+format(option, '02x')))
    out = ser.read()
    ser.write(bytearray.fromhex("4B01C8"+color[1]+format(option+32, '02x')))
    out = ser.read()

def candlelight(ser, color):
    global initial
    for array in initial:
        ser.write(array)
        out = ser.read()
        pass

    ser.write(bytearray.fromhex("4B01CC"+color+"00"))
    out = ser.read()

if args.command == "fixed":
    fixed(ser, args.color)
elif args.command == 'breathing':
    breathing(ser, args.colors, args.speed)
elif args.command == 'fading':
    fading(ser, args.colors, args.speed)
elif args.command == 'marquee':
    marquee(ser, args.colors, args.speed, args.size, args.comet, args.backwards)
elif args.command == 'cover_marquee':
    cover_marquee(ser, args.colors, args.speed, args.backwards)
elif args.command == 'pulse':
    pulse(ser, args.colors, args.speed)
elif args.command == 'spectrum':
    spectrum(ser, args.speed, args.backwards)
elif args.command == 'alternating':
    alternating(ser, args.colors, args.speed, args.size, args.moving, args.backwards)
elif args.command == 'candlelight':
    candlelight(ser, args.color)
else:
    print("INVALID COMMAND")
    sys.exit(-1)
