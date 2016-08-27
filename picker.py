#!/usr/bin/env python3
import subprocess

def RGBToHTMLColor(rgb_tuple):
    """ convert an (R, G, B) tuple to #RRGGBB """
    hexcolor = '%02x%02x%02x' % rgb_tuple
    # that's it! '%02x' means zero-padded, 2-digit hex values
    return hexcolor.upper()

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

out = subprocess.check_output(['zenity', '--color-selection']).decode("utf-8")
if out != "":
    rgb = tuple(map(int, find_between(out, "rgb(", ")").split(',')))
    print(RGBToHTMLColor(rgb))
