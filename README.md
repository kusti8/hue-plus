# hue-plus
A Linux driver in Python for the NZXT Hue+
## Install
To install it system wide, simply run install.sh as root `sudo ./install.sh`
Now it will be available as `hue` and `hue-picker`
**To use the GUI you must have zenity installed**
## Usage
```
usage: hue [-h] [-p PORT] [-c CHANNEL] [-g GUI]
           {fixed,breathing,fading,marquee,cover_marquee,pulse,spectrum,alternating,candlelight,power}
           ...

Change NZXT Hue+ LEDs

positional arguments:
  {fixed,breathing,fading,marquee,cover_marquee,pulse,spectrum,alternating,candlelight,power}
                        The type of color (fixed, breathing)
    fixed               One single fixed color
    breathing           Breathing through a set of colors
    fading              Fading through a set of colors
    marquee             A strip of color running
    cover_marquee       A strip of color running (multiple colors)
    pulse               Pulsing through a set of colors
    spectrum            Pulsing through a set of colors
    alternating         Two alternating colors
    candlelight         A flickering color
    power               Control power to the channels

optional arguments:
  -h, --help            show this help message and exit
  -p PORT, --port PORT  The port, defaults to /dev/ttyACM0
  -c CHANNEL, --channel CHANNEL
                        The channel, defaults to 1
  -g GUI, --gui GUI     How many colors of GUI picker
```
And then to have a simple color picker (you must have zenity installed):
`hue-picker`

*The default hue.py now includes the color selector, simply set -g to however many colors you want*
## Limitations
No Audio, FPS, CPU temp, GPU temp or Custom, but other than that a perfect replica.

## Warning
  I (the author) hold no liability for any broken or not working Hue+ by running this script. It is provided as is. It worked for me, but your milage may vary
