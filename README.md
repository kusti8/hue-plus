# hue-plus
## Now with audio sync support!
A Linux driver in Python for the NZXT Hue+

![Fixed](https://github.com/kusti8/hue-plus/raw/master/fixed.png)
![Alternating](https://github.com/kusti8/hue-plus/raw/master/alternating.png)
## Install
To install it system wide, simply run install.sh as root `sudo ./install.sh`

Now it will be available as `hue` and `hue-picker` or `hue-ui` for the GUI.
**To use the GUI you must have zenity and PyQt5 installed. Ex: `sudo apt-get install zenity python-pyqt5`**

### Arch Linux
Arch Linux users can install hue-plus from the AUR: https://aur.archlinux.org/packages/hue-plus-git/

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
```
usage: hue [-h] [-p PORT] [-c CHANNEL] [-g GUI]
           {fixed,breathing,fading,marquee,cover_marquee,pulse,spectrum,alternating,candlelight,wings,audio_level,power}
           ...

Change NZXT Hue+ LEDs

positional arguments:
  {fixed,breathing,fading,marquee,cover_marquee,pulse,spectrum,alternating,candlelight,wings,audio_level,power}
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
    wings               Strips of light meeting in the center
    audio_level         Light syncronized to music levels
    power               Control power to the channels

optional arguments:
  -h, --help            show this help message and exit
  -p PORT, --port PORT  The port, defaults to /dev/ttyACM0
  -c CHANNEL, --channel CHANNEL
                        The channel, defaults to 0 (BOTH)
  -g GUI, --gui GUI     How many colors of GUI picker
```
### Fixed
```
usage: hue fixed [-h] color

positional arguments:
  color       Color in hex

optional arguments:
  -h, --help  show this help message and exit
```
### Breathing
```
usage: hue breathing [-h] speed colors [colors ...]

positional arguments:
  speed       Speed from 0(Slowest) to 4(Fastest)
  colors      Color(s) in hex

optional arguments:
  -h, --help  show this help message and exit
```
### Fading
```
usage: hue fading [-h] speed colors [colors ...]

positional arguments:
  speed       Speed from 0(Slowest) to 4(Fastest)
  colors      Color(s) in hex

optional arguments:
  -h, --help  show this help message and exit
```
### Marquee
```
usage: hue marquee [-h] [-b] speed size color

positional arguments:
  speed            Speed from 0(Slowest) to 4(Fastest)
  size             The size of the group of runners (0=3, 1=4, 2=5, 3=6)
  color            Foreground color in hex

optional arguments:
  -h, --help       show this help message and exit
  -b, --backwards  Enable going backwards
```
### Covering Marquee
```
usage: hue cover_marquee [-h] [-b] speed colors [colors ...]

positional arguments:
  speed            Speed from 0(Slowest) to 4(Fastest)
  colors           Colors in hex

optional arguments:
  -h, --help       show this help message and exit
  -b, --backwards  Enable going backwards
```
### Pulse
```
usage: hue pulse [-h] speed colors [colors ...]

positional arguments:
  speed       Speed from 0(Slowest) to 4(Fastest)
  colors      Color(s) in hex

optional arguments:
  -h, --help  show this help message and exit
```
### Spectrum
```
usage: hue spectrum [-h] [-b] speed

positional arguments:
  speed            Speed from 0(Slowest) to 4(Fastest)

optional arguments:
  -h, --help       show this help message and exit
  -b, --backwards  Enable going backwards
```
### Alternating
```
usage: hue alternating [-h] [-m] [-b] speed size colors colors

positional arguments:
  speed            Speed from 0(Slowest) to 4(Fastest)
  size             The size of the group of runners (0=2, 1=3, 2=5, 3=10)
  colors           First and second colors in hex

optional arguments:
  -h, --help       show this help message and exit
  -m, --moving     Enable movement
  -b, --backwards  Enable going backwards (requires movement)
```
### Candlelight
```
usage: hue candlelight [-h] color

positional arguments:
  color       Color in hex

optional arguments:
  -h, --help  show this help message and exit
```
### Wings
```
usage: hue wings [-h] speed color

positional arguments:
  speed       Speed from 0(Slowest) to 4(Fastest)
  color       Color in hex

optional arguments:
  -h, --help  show this help message and exit
```
### Audio (requires PyAudio and nonroot)
```
usage: hue audio_level [-h] tolerance refresh colors [colors ...]

positional arguments:
  tolerance   The maximum audio level ie. when the audio is as loud as
              tolerance, all LEDs will be lit
  refresh     The speed of refreshing the LEDs (usually 5 is a good number)
  colors      Colors in hex, starting from lowest volume to highest

optional arguments:
  -h, --help  show this help message and exit
```
### Power
```
usage: hue power [-h] state

positional arguments:
  state       State (on/off)

optional arguments:
  -h, --help  show this help message and exit
```


And then to have a simple color picker (you must have zenity installed):
`hue-picker`

*The default hue.py now includes the color selector, simply set -g to however many colors you want*
## Limitations
No Audio, FPS, CPU temp, GPU temp or Custom, but other than that a perfect replica.

## Warning
  I (the author) hold no liability for any broken or not working Hue+ by running this script. It is provided as is. It worked for me, but your milage may vary
