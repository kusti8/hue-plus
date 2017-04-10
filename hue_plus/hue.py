#!/usr/bin/env python3
import serial
import time
from time import sleep
import sys
import argparse
import os
from . import picker
from . import previous
import sys
import struct
import math
import colorsys

def main():
    #if os.geteuid() != 0:
    #    sys.exit("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'.")

    parser = argparse.ArgumentParser(description="Change NZXT Hue+ LEDs")
    parser.add_argument("-p", "--port", default="/dev/ttyACM0", type=str, help="The port, defaults to /dev/ttyACM0")
    parser.add_argument("-c", "--channel", type=int, default=0, help="The channel, defaults to 0 (BOTH)")
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
    parser_marquee.add_argument("-b", "--backwards", action="store_const", const=0, default=0, help="Enable going backwards")
    parser_marquee.add_argument("size", type=int, help="The size of the group of runners (0=3, 1=4, 2=5, 3=6)")
    parser_marquee.add_argument("color", type=str, help="Foreground color in hex")

    parser_cover_marquee = subparsers.add_parser('cover_marquee', help="A strip of color running (multiple colors)")
    parser_cover_marquee.add_argument("speed", type=int, help="Speed from 0(Slowest) to 4(Fastest)")
    parser_cover_marquee.add_argument("-b", "--backwards", action="store_const", const=0, default=0, help="Enable going backwards")
    parser_cover_marquee.add_argument("colors", type=str, nargs='+', help="Colors in hex")

    parser_pulse = subparsers.add_parser('pulse', help="Pulsing through a set of colors")
    parser_pulse.add_argument("speed", type=int, help="Speed from 0(Slowest) to 4(Fastest)")
    parser_pulse.add_argument("colors", type=str, nargs='+', help="Color(s) in hex")

    parser_spectrum = subparsers.add_parser('spectrum', help="Pulsing through a set of colors")
    parser_spectrum.add_argument("speed", type=int, help="Speed from 0(Slowest) to 4(Fastest)")
    parser_spectrum.add_argument("-b", "--backwards", action="store_const", const=1, default=0, help="Enable going backwards")

    parser_alternating = subparsers.add_parser('alternating', help="Two alternating colors")
    parser_alternating.add_argument("speed", type=int, help="Speed from 0(Slowest) to 4(Fastest)")
    parser_alternating.add_argument("-m", "--moving", action="store_true", help="Enable movement")
    parser_alternating.add_argument("-b", "--backwards", action="store_const", const=1, default=0, help="Enable going backwards (requires movement)")
    parser_alternating.add_argument("size", type=int, help="The size of the group of runners (0=2, 1=3, 2=5, 3=10)")
    parser_alternating.add_argument("colors", type=str, nargs=2, help="First and second colors in hex")

    parser_candlelight = subparsers.add_parser('candlelight', help="A flickering color")
    parser_candlelight.add_argument("color", type=str, help="Color in hex")

    parser_wings = subparsers.add_parser('wings', help="Strips of light meeting in the center")
    parser_wings.add_argument("speed", type=int, help="Speed from 0(Slowest) to 4(Fastest)")
    parser_wings.add_argument("color", type=str, help="Color in hex")

    parser_audio_level = subparsers.add_parser('audio_level', help="Light syncronized to music levels")
    parser_audio_level.add_argument("tolerance", type=float, help="The maximum audio level ie. when the audio is as loud as tolerance, all LEDs will be lit")
    parser_audio_level.add_argument("refresh", type=int, help="The speed of refreshing the LEDs (usually 5 is a good number)")
    parser_audio_level.add_argument("colors", type=str, nargs='+', help="Colors in hex, starting from lowest volume to highest")

    parser_power = subparsers.add_parser('power', help="Control power to the channels")
    parser_power.add_argument("state", type=str, help="State (on/off)")

    args = parser.parse_args()

    ser = serial.Serial(args.port, 256000)

    if args.command == "fixed":
        fixed(ser, args.gui, args.channel, args.color)
    elif args.command == 'breathing':
        breathing(ser, args.gui, args.channel, args.colors, args.speed)
    elif args.command == 'fading':
        fading(ser, args.gui, args.channel, args.colors, args.speed)
    elif args.command == 'marquee':
        marquee(ser, args.gui, args.channel, args.color, args.speed, args.size, args.backwards)
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
    elif args.command == 'wings':
        wings(ser, args.gui, args.channel, args.color, args.speed)
    elif args.command == 'audio_level':
        audio_level(ser, args.gui, args.channel, args.colors, args.tolerance, args.refresh)
    elif args.command == 'power':
        power(ser, args.channel, args.state)
    else:
        print("INVALID COMMAND")
        sys.exit(-1)

def write_audio(ser, channel, colors, tolerance, value, strips):
    try:
        if value >= tolerance: # Prevent index out of range
            value = tolerance
        elif value < 0.0:
            value = 0.0
        normal = (value/tolerance)*int(strips[channel-1]*10)
        normal_color = (value/tolerance)*len(colors)
        size = int(strips[channel-1]*10/len(colors))
        value = normal_color*size-int(normal_color*size) # Get value fraction
        dis = colors[:int(normal_color)]
        display = []
        for color in dis:
            for i in range(int(size)):
                display.append(color)
        for i in range(int(value*size)):
            display.append(colors[int(normal_color)])
        rgb = colors[int(normal_color)]
        rgb = (int(rgb[:2], 16)/255.0, int(rgb[2:4], 16)/255.0, int(rgb[4:], 16)/255.0)
        h, s, v = colorsys.rgb_to_hsv(*rgb)
        v = value*v # Change value of final color
        r,g,b = colorsys.hsv_to_rgb(h, s, v)
        r = int(r*255)
        g = int(g*255)
        b = int(b*255)
        hexcolor = '%02x%02x%02x' % (r,g,b) # Back to html notation
        display.append(hexcolor.upper())
    except KeyboardInterrupt:
        raise
    except:
        return
    command = create_custom(ser, channel, display, "audio", 0, 0, 0, 0, strips)
    outputs = previous.get_colors(channel, command)
    write(ser, outputs)

def audio_level(ser, gui, channel, colors, tolerance, smooth):
    if os.geteuid() == 0:
        sys.exit("Audio won't work with root. Login as a normal user, add your user to the group of /dev/ttyACM0 and retry without root")
    if 1 <= gui <= 8:
        colors = []
        for i in range(gui):
            colors.append(picker.pick("Color "+str(i+1) + " of "+str(gui)))
    strips = [strips_info(ser, 1), strips_info(ser, 2)]
    if channel == 0:
        channel = [1, 2]
    else:
        channel = [channel]
    init(ser)
    import pyaudio
    import wave

    chunk = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    RECORD_SECONDS = 500000
    WAVE_OUTPUT_FILENAME = "output.wav"
    p = pyaudio.PyAudio()
    stream = p.open(format = FORMAT,
                    channels = CHANNELS,
                    rate = RATE,
                    input = True,
                    output = True,
                    frames_per_buffer = chunk)
    alls = []
    s = []
    try:
        while True:
            try:
                data = stream.read(chunk)
            except IOError:
                continue
            alls.append(data)
            if len(alls)>1:
                data = b''.join(alls)
                wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(p.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(data)
                wf.close()
                w = wave.open(WAVE_OUTPUT_FILENAME, 'rb')
                summ = 0
                value = 1
                delta = 1
                amps = [ ]
                for i in range(0, w.getnframes()):
                    data = struct.unpack('<h', w.readframes(1))
                    summ += (data[0]*data[0]) / 2
                    if (i != 0 and (i % 1470) == 0):
                        value = int(math.sqrt(summ / 1470.0) / 10)
                        amps.append(value - delta)
                        summ = 0
                        tarW=float(amps[0]*1.0/delta/100)
                        s.append(tarW)
                        if len(s) >= smooth:
                            out = sum(s)/len(s)
                            for c in channel:
                                write_audio(ser, c, colors, tolerance, out, strips)
                            s = []
                        delta = value
                alls=[]
    except:
        stream.close()
        p.terminate()
        os.remove(WAVE_OUTPUT_FILENAME)
        raise

def create_custom(ser, channel, colors, mode, direction, option, group, speed, strips):
    if colors == None:
        colors = []

    commands = []
    channel_commands = []
    modes = {
        "audio": 14
    }
    if modes[mode] != 14: # Audio flickers when initing, not needed
        init(ser)

    strips = [0, strips[0]-1, strips[1]-1]
    strips[0] = max(strips)

    if channel == 0:
        channels = [1, 2]
    else:
        channels = [channel]

    for channela in channels:
        command = []
        command.append(75)
        command.append(channela)
        command.append(modes[mode])
        command.append(direction << 4 | option << 3 | strips[channela])
        command.append(0 << 5 | group << 3 | speed)
        for color in colors:
            command.append(int(color[2:4], 16))
            command.append(int(color[:2], 16))
            command.append(int(color[4:], 16))
        for z in range(40-len(colors)):
            command.append(0)
            command.append(0)
            command.append(0)
        command = bytearray(command)
        channel_commands.append([command])
    return channel_commands


def create_command(ser, channel, colors, mode, direction, option, group, speed):
    init(ser)

    commands = []
    channel_commands = []
    modes = {
        "fixed": 0,
        "breathing": 7,
        "fading": 1,
        "marquee": 3,
        "cover_marquee": 4,
        "pulse": 6,
        "spectrum": 2,
        "alternating": 5,
        "candlelight": 9,
        "wings": 12,
        "wave": 13,
        "alert": 8
    }

    strips = [0, strips_info(ser, 1)-1, strips_info(ser, 2)-1]
    strips[0] = max(strips)

    if channel == 0:
        channels = [1, 2]
    else:
        channels = [channel]

    for channela in channels:
        commands = []
        for i, color in enumerate(colors):
            command = []
            command.append(75)
            command.append(channela)
            command.append(modes[mode])
            command.append(direction << 4 | option << 3 | strips[channela])
            command.append(i << 5 | group << 3 | speed)
            for z in range(40):
                command.append(int(color[2:4], 16))
                command.append(int(color[:2], 16))
                command.append(int(color[4:], 16))
            command = bytearray(command)
            commands.append(command)

        channel_commands.append(commands)
    return channel_commands


def strips_info(ser, channel):
    time.sleep(0.2)
    out = bytearray.fromhex("8D0" + str(channel))
    ser.write(out)
    time.sleep(1)
    out = ser.read(ser.in_waiting).hex()
    if out:
        r = int(out[-1])
    else:
        r = -1
    if r <= 0:
        r = 1
    return r


def init(ser):
    C0(ser)
    # Took out bytearray([70, 0, 192, 0, 0, 0, 255])
    initial = [bytearray.fromhex("4B" + "00"*124)]
    for array in initial:
        ser.write(array)
        time.sleep(0.2)
        ser.read(ser.in_waiting)

def C0(ser):
    while True:
        ser.write(bytearray.fromhex("C0"))
        if ser.in_waiting != 0:
            ser.read()
            break

def write(ser, outputs):
    for channel in outputs:
        for line in channel:
            if line:
                ser.write(line)
                ser.read()


def fixed(ser, gui, channel, color):

    if gui != 0:
        color = picker.pick("Color")

    command = create_command(ser, channel, [color], "fixed", 0, 0, 0, 2)
    outputs = previous.get_colors(channel, command)
    write(ser, outputs)


def breathing(ser, gui, channel, color, speed):

    if 1 <= gui <= 8:
        color = []
        for i in range(gui):
            color.append(picker.pick("Color "+str(i+1) + " of "+str(gui)))

    command = create_command(ser, channel, color, "breathing", 0, 0, 0, speed)

    outputs = previous.get_colors(channel, command)
    write(ser, outputs)


def fading(ser, gui, channel, color, speed):

    if 1 <= gui <= 8:
        color = []
        for i in range(gui):
            color.append(picker.pick("Color "+str(i+1) + " of "+str(gui)))

    command = create_command(ser, channel, color, "fading", 0, 0, 0, speed)

    outputs = previous.get_colors(channel, command)
    write(ser, outputs)


def marquee(ser, gui, channel, color, speed, size, direction):

    if gui != 0:
        gui = 1
        for i in range(1):
            color = picker.pick("Color "+str(i+1) + " of "+str(gui))

    command = create_command(ser, channel, [color], "marquee", direction, 0, size, speed)
    outputs = previous.get_colors(channel, command)
    write(ser, outputs)


def cover_marquee(ser, gui, channel, color, speed, direction):

    if 1 <= gui <= 8:
        color = []
        for i in range(gui):
            color.append(picker.pick("Color "+str(i+1) + " of "+str(gui)))

    command = create_command(ser, channel, color, "cover_marquee", direction, 0, 0, speed)
    outputs = previous.get_colors(channel, command)
    write(ser, outputs)


def pulse(ser, gui, channel, color, speed):

    if 1 <= gui <= 8:
        color = []
        for i in range(gui):
            color.append(picker.pick("Color "+str(i+1) + " of "+str(gui)))

    command = create_command(ser, channel, color, "pulse", 0, 0, 0, speed)
    outputs = previous.get_colors(channel, command)
    write(ser, outputs)


def spectrum(ser, channel, speed, direction):

    command = create_command(ser, channel, ["0000FF"], "spectrum", direction, 0, 0, speed)

    outputs = previous.get_colors(channel, command)
    write(ser, outputs)


def alternating(ser, gui, channel, color, speed, size, moving, direction):

    if gui != 0:
        color = []
        gui = 2
        for i in range(2):
            color.append(picker.pick("Color "+str(i+1) + " of "+str(gui)))

    if moving:
        option = 1
    else:
        option = 0

    command = create_command(ser, channel, color, "alternating", direction, option, size, speed)
    outputs = previous.get_colors(channel, command)
    write(ser, outputs)


def candlelight(ser, gui, channel, color):

    if gui != 0:
        color = picker.pick("Color")

    command = create_command(ser, channel, [color], "candlelight", 0, 0, 0, 0)

    outputs = previous.get_colors(channel, command)
    write(ser, outputs)


def wings(ser, gui, channel, color, speed):

    if gui != 0:
        color = picker.pick("Color")

    command = create_command(ser, channel, [color], "wings", 0, 0, 0, speed)
    outputs = previous.get_colors(channel, command)
    write(ser, outputs)


def power(ser, channel, state):
    if state.lower() == 'on':
        fixed(ser, 0, channel, "FFFFFF")
    elif state.lower() == 'off':
        fixed(ser, 0, channel, "000000")
    else:
        print("INVALID STATE!")
        sys.exit(-1)

if __name__ == '__main__':
    main()
