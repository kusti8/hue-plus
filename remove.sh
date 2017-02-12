#!/bin/bash

# A simple script to uninstall hue-plus to a universally availible location (in the path)

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

rm /usr/bin/hue
rm /usr/bin/hue-picker
rm /usr/bin/hue-ui

rm -r /var/lib/hue-plus

echo "Now it's uninstalled!"
