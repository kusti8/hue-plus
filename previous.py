import sys


def get_colors(channel, changer):
    with open('/var/lib/hue-plus/previous', 'r+') as prefs:
        if channel == 0:
            return changer
        elif channel == 1:
            return (changer, prefs[1])  # Return the original one channel and the previous second channel
        elif channel == 2:
            return (prefs[0], changer)

if __name__ == '__main__':
    sys.exit(0)
