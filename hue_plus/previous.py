"""Functions to handle the previous colors

Obtains previous colors from file and returns them
"""
import sys
import os
import shutil
import pickle
from appdirs import *

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

path = os.path.join(determine_path(), "things", "previous.p")
local = user_data_dir('hue_plus', 'kusti8')
if not os.path.exists(local):
    os.makedirs(local)
local = os.path.join(local, 'previous.p')
if not os.path.isfile(local):
    shutil.copyfile(path, local)
path = local

def changer_to_two(changer):
    line1 = []
    line2 = []
    for line in changer:
        line1.append(line[:3] + '1' + line[4:])
        line2.append(line[:3] + '2' + line[4:])
    write(line1, line2)
    return [line1, line2]


def write(line1, line2, profiles):
    global path
    pickle.dump(([line1, line2], profiles), open(path, 'wb'))

def read():
    global path
    out = pickle.load(open(path, 'rb'))
    if type(out) is tuple:
        return out
    else:
        return (out, {})


def get_colors(channel, changer):
    """Get the previous colors stored so channel 2 stays the same"""
    data, profiles = read()
    if channel == 0:
        #print(changer)
        # Changer[0] is list of commands for first channel
        write(changer[0], changer[1], profiles)
        return [changer[0], changer[1]]
    elif channel == 1:
        write(changer[0], data[1], profiles)
        return [changer[0], data[1]]  # Return the original one channel and the previous second channel
    elif channel == 2:
        write(data[0], changer[0], profiles)
        return [data[0], changer[0]]

def get_previous():
    data, profiles = read()
    return data

def add_profile(name):
    data, profiles = read()
    profiles[name] = data
    write(data[0], data[1], profiles)

def list_profile():
    data, profiles = read()
    return(list(profiles))

def rm_profile(name):
    data, profiles = read()
    try:
        del profiles[name]
    except:
        pass
    write(data[0], data[1], profiles)

def apply_profile(name):
    data, profiles = read()
    try:
        return profiles[name]
    except:
        pass


if __name__ == '__main__':
    sys.exit(0)
