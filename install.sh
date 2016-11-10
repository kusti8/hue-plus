#!/bin/bash

# A simple script to install hue-plus to a universally availible location (in the path)

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

pip3 install pyserial

ln -s $(pwd)/hue.py /usr/bin/hue
ln -s $(pwd)/picker.py /usr/bin/hue-picker

mkdir /var/lib/hue-plus
cp previous.p /var/lib/hue-plus/previous.p

echo "Now you can run 'hue' or 'hue-picker' from anywhere!"
