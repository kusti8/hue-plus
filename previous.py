"""Functions to handle the previous colors

Obtains previous colors from file and returns them
"""
import sys
import os
import shutil
import pickle

path = '/var/lib/hue-plus/previous.p'
if os.path.isfile(path):
    shutil.copyfile('previous.p', path)


def changer_to_two(changer):
    line1 = []
    line2 = []
    for line in changer:
        line1.append(changer[:3] + '1' + changer[4:])
        line2.append(changer[:3] + '2' + changer[4:])
    return (line1, line2)


def write(line1, line2):
    global path
    pickle.dump([line1, line2], open(path, 'wb'))


def get_colors(channel, changer):
    """Get the previous colors stored so channel 2 stays the same"""
    data = pickle.load(open(path, 'rb'))
    if channel == 0:
        return [changer]
        write(*changer_to_two(changer))
    elif channel == 1:
        return [changer, data[1]]  # Return the original one channel and the previous second channel
        write(changer, data[1])
    elif channel == 2:
        return [data[0], changer]
        write(data[0], changer)


if __name__ == '__main__':
    sys.exit(0)
