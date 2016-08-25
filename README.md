# hue-plus
A Linux driver in Python for the NZXT Hue+
## Usage
```
usage: hue.py [-h] [-p PORT] [-c CHANNEL]
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
```
## Limitations
No Audio, FPS, CPU temp, GPU temp or Custom, but other than that a perfect replica.

## Warning
  I (the author) hold no liability for any broken or not working Hue+ by running this script. It is provided as is. It worked for me, but your milage may vary
