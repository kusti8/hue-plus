"""Functions to handle the previous colors

Obtains previous colors from file and returns them
"""
import sys
import os
import shutil
import pickle
from appdirs import *
from PyQt5.QtCore import QSettings

package_import = True
if package_import:
    from . import webcolors
else:
    import webcolors

settings = QSettings('kusti8', 'hue_plus')

def write(line1='None', line2='None', profiles='None', times='None', customs='None'):
    global settings
    if line1 != 'None':
        settings.setValue('line1', line1)
    if line2 != 'None':
        settings.setValue('line2', line2)
    if profiles != 'None':
        settings.setValue('profiles', profiles)
    if times != 'None':
        settings.setValue('times', times)
    if customs != 'None':
        settings.setValue('customs', customs)

def read():
    global settings
    out = {}
    for i in ['line1', 'line2', 'profiles', 'times', 'customs']:
        out[i] = settings.value(i)
    return out


def get_colors(channel, changer):
    """Get the previous colors stored so channel 2 stays the same"""
    if channel == 0:
        #print(changer)
        # Changer[0] is list of commands for first channel
        write(changer[0], changer[1])
        return [changer[0], changer[1]]
    elif channel == 1:
        line2 = read()['line2']
        write(changer[0], line2)
        return [changer[0], line2]  # Return the original one channel and the previous second channel
    elif channel == 2:
        line1 = read()['line1']
        write(line1, changer[0])
        return [line1, changer[0]]

def get_previous():
    data = [read()['line1'], read()['line2']]
    return data

def add_profile(name):
    data = [read()['line1'], read()['line2']]
    profiles = read()['profiles']
    profiles[name] = data
    write(data[0], data[1], profiles)

def list_profile():
    profiles = read()['profiles']
    customs = read()['customs']
    if profiles:
        p = list(profiles)
        if customs:
            p.append(customs['name'])
            return p
        else:
            return p
    else:
        return []

def rm_profile(name):
    profiles = read()['profiles']
    customs = read()['customs']
    try:
        del profiles[name]
    except:
        if customs:
            customs = {}
    write(profiles=profiles, customs=customs)

def apply_profile(name):
    profiles = read()['profiles']
    customs = read()['customs']
    try:
        return profiles[name]
    except:
        if customs:
            return customs

def get_times():
    times = read()['times']
    return times

def apply_times(time):
    write(times=time)

def init():
    global settings
    out = read()
    if not out['line1']:
        write(line1=[bytearray(b'K\x01\x02\x02\x04\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff')])
    if not out['line2']:
        write(line2=[bytearray(b'K\x02\x02\x00\x04\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff\x00\x00\xff')])
    if not out['profiles']:
        write(profiles={})
    if not out['times']:
        write(times=['00:00', '00:00'])
    if not out['customs']:
        write(customs={})

init()


if __name__ == '__main__':
    sys.exit(0)
