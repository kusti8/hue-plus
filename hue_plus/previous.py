"""Functions to handle the previous colors

Obtains previous colors from file and returns them
"""
import sys
import os
import shutil
import pickle

from . import webcolors

def determine_path():
    """Borrowed from wxglade.py"""
    try:
        root = __file__
        if os.path.islink(root):
            root = os.path.realpath(root)
        return os.path.dirname (os.path.abspath(root))
    except:
        print("I'm sorry, but something is wrong.")
        print("There is no __file__ variable. Please contact the author.")
        sys.exit()

path = determine_path() + "/things/previous.p"
if 'site-packages' not in path: # Windows EXE install
    path = os.getenv('APPDATA') + '/hue_plus/previous.p'
    if not os.path.exists(os.getenv('APPDATA')+'/hue_plus'):
        os.makedirs(os.getenv('APPDATA')+'/hue_plus')
    if not os.path.isfile(path):
        shutil.copyfile(determine_path()+'/things/previous.p', path)

def changer_to_two(changer):
    line1 = []
    line2 = []
    for line in changer:
        line1.append(line[:3] + '1' + line[4:])
        line2.append(line[:3] + '2' + line[4:])
    write(line1, line2)
    return [line1, line2]


def write(line1, line2):
    global path
    pickle.dump([line1, line2], open(path, 'wb'))


def get_colors(channel, changer):
    """Get the previous colors stored so channel 2 stays the same"""
    data = pickle.load(open(path, 'rb'))
    if channel == 0:
        #print(changer)
        # Changer[0] is list of commands for first channel
        write(changer[0], changer[1])
        return [changer[0], changer[1]]
    elif channel == 1:
        write(changer[0], data[1])
        return [changer[0], data[1]]  # Return the original one channel and the previous second channel
    elif channel == 2:
        write(data[0], changer[0])
        return [data[0], changer[0]]


if __name__ == '__main__':
    sys.exit(0)
