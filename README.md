# hue-plus
## Now with custom LED, audio mode on Windows, turning on and off based on time, and a custom mode builder and a developer library, plus bug fixes!
Support me on patreon: https://www.patreon.com/kusti8

[![Build status](https://ci.appveyor.com/api/projects/status/5u1902hw1hqtlldb?svg=true)](https://ci.appveyor.com/project/kusti8/hue-plus)

A **cross-platform** driver in Python for the NZXT Hue+. Supports **all functionality** except FPS, CPU, and GPU lighting.

![Custom](https://github.com/kusti8/hue-plus/raw/master/custom.png)
![Windows](https://github.com/kusti8/hue-plus/raw/master/windows.png)
![Profile](https://github.com/kusti8/hue-plus/raw/master/profile.png)
## Install
### Windows
There is always an easy exe installer available here:
https://github.com/kusti8/hue-plus/releases/latest
### Linux
You must have `python3-dev` and `portaudio19-dev` installed!
To install it system wide, simply install using pip:
```
sudo pip3 install hue_plus
```
Now it will be available as `hue` or `hue_ui` for the GUI.

## Quick Start
Each mode accepts different arguments, so it's easiest to just read the usage.
Basic usage is shown below.
### Set a fixed color on all channels
`sudo hue fixed FFFFFF` where FFFFFF is the color in hex.

*or*

`sudo hue -g 1 fixed FFFFFF` will bring up a color picker to choose a color
### Set a specific channel
`sudo hue -c 1 fixed FFFFFF` where 1 is channel one and 2 is channel two
## Usage
All help and usage can be found by running ``hue -h``

*The default hue.py now includes the color selector, simply set -g to however many colors you want*
## Limitations
No FPS, CPU temp, or GPU temp, but other than that a perfect replica.

## Developers
Hue_plus can easily be integrated into existing software. The entire codebase is separated into simple functions that separate all usage and can be directly called. The script provides a simple argument wrapper around them, but they are easily usable. **I highly suggest you read through the main ``hue.py`` file, specifically ``hue.main()`` to get acquianted with how to use it. Each function is slightly different.**

### Quickstart

```
import serial
import hue_plus

ser = serial.Serial(args.port, 256000)
hue_plus.fixed(ser, 0, 0, 'FF0000') # First argument is ser, second is whether to bring up GUI (0=no), third is channel (0=both) and last is the color
```

### Common args

Argument name | Description
--- | ---
ser | The serial object, created as shown above
gui | How many colors to select in the GUI, 0 is none
channel | The channel number to use, 1 or 2, 0 is both
color(s) | The color(s) to use. If accepts more than 1 color, then in a list (`['FF0000', '00FF00']`)
speed | The speed, from 0 (Slowest) to 4 (Fastest). 2 is normal
size | The amount of LEDs to shine, from 0-3, where 0=3, 1=4, 2=5, 3=6
direction | Supports going backwards, where backwards=1 and forwards=0. **Not supported in marquee or cover_marquee**
moving | `true` or `false` if alternating looks like it is moving
state | For power mode, either `'on'` or `'off'`
mode | For custom mode, either `'fixed'`, `'breathing'`, or `'wave'`

## Notes

Hue-plus does not automatically run on startup. This will not be added as a feature, but you should do this manually if you want that. For windows, follow this: http://www.thewindowsclub.com/make-programs-run-on-startup-windows. For Mac/Linux, use cron.

## Warning
  I (the author) hold no liability for any broken or not working Hue+ by running this script. It is provided as is. It worked for me, but your milage may vary
