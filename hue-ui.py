#!/usr/bin/env python3
import sys
import os
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QGridLayout, QLabel, QLineEdit, QMessageBox
from PyQt5.QtWidgets import QTextEdit, QWidget, QMainWindow, QApplication, QListWidgetItem

import hue_gui
import picker
import hue
import serial

import webcolors

def closest_colour(requested_colour):
    min_colours = {}
    for key, name in webcolors.css3_hex_to_names.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - requested_colour[0]) ** 2
        gd = (g_c - requested_colour[1]) ** 2
        bd = (b_c - requested_colour[2]) ** 2
        min_colours[(rd + gd + bd)] = name
    return min_colours[min(min_colours.keys())]

def get_colour_name(requested_colour):
    try:
        closest_name = actual_name = webcolors.rgb_to_name(requested_colour)
    except ValueError:
        closest_name = closest_colour(requested_colour)
        actual_name = None
    return actual_name, closest_name

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

class MainWindow(QMainWindow, hue_gui.Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)

        self.indexApply = {
            0: self.fixedApply,
            1: self.breathingApply,
            2: self.fadingApply,
            3: self.marqueeApply,
            4: self.coverMarqueeApply,
            5: self.pulseApply,
            6: self.spectrumApply,
            7: self.alternatingApply,
            8: self.candleApply,
            9: self.wingsApply,
            10: self.audioLevelApply
            }

        self.fixedAdd.clicked.connect(self.fixedAddFunc)
        self.fixedDelete.clicked.connect(self.fixedDeleteFunc)
        self.breathingAdd.clicked.connect(self.breathingAddFunc)
        self.breathingDelete.clicked.connect(self.breathingDeleteFunc)
        self.fadingAdd.clicked.connect(self.fadingAddFunc)
        self.fadingDelete.clicked.connect(self.fadingDeleteFunc)
        self.marqueeAdd.clicked.connect(self.marqueeAddFunc)
        self.marqueeDelete.clicked.connect(self.marqueeDeleteFunc)
        self.coverMarqueeAdd.clicked.connect(self.coverMarqueeAddFunc)
        self.coverMarqueeDelete.clicked.connect(self.coverMarqueeDeleteFunc)
        self.pulseAdd.clicked.connect(self.pulseAddFunc)
        self.pulseDelete.clicked.connect(self.pulseDeleteFunc)
        self.alternatingAdd.clicked.connect(self.alternatingAddFunc)
        self.alternatingDelete.clicked.connect(self.alternatingDeleteFunc)
        self.candleAdd.clicked.connect(self.candleAddFunc)
        self.candleDelete.clicked.connect(self.candleDeleteFunc)
        self.wingsAdd.clicked.connect(self.wingsAddFunc)
        self.wingsDelete.clicked.connect(self.wingsDeleteFunc)
        self.audioLevelAdd.clicked.connect(self.audioLevelAddFunc)
        self.audioLevelDelete.clicked.connect(self.audioLevelDeleteFunc)
        self.applyBtn.clicked.connect(self.applyFunc)

    def error(self, message):
        msg = QMessageBox()
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.Ok)
        out = msg.exec_()

    def getChannel(self):
        if self.channel1Check.isChecked() and self.channel2Check.isChecked():
            return 0
        elif self.channel1Check.isChecked():
            return 1
        elif self.channel2Check.isChecked():
            return 2
        else:
            return None

    def getColors(self, modeList):
        colors = []
        for i in range(modeList.count()):
            colors.append(find_between(modeList.item(i).text(), '#', ')').upper())
        if modeList.count() == 0:
            self.error("Must have at least one color")
            return ['FF0000']
        return colors

    ## Fixed
    def fixedAddFunc(self):
        if self.fixedList.count() == 1:
            self.error("Fixed cannot have more than one color")
        else:
            color = "#" + picker.pick("Color").lower()
            actual, closest = get_colour_name(webcolors.hex_to_rgb(color))
            if not actual:
                actual = closest
            self.fixedList.addItem(QListWidgetItem(actual + "(" + color + ")"))

    def fixedDeleteFunc(self):
        self.fixedList.takeItem(self.fixedList.currentRow())

    def fixedApply(self):
        with serial.Serial(self.portTxt.text(), 256000) as ser:
            print("Applying")
            if self.getChannel() == None:
                hue.power(ser, 0, "off")
            else:
                print(self.getColors(self.fixedList)[0], self.getChannel())
                hue.fixed(ser, 0, self.getChannel(), self.getColors(self.fixedList)[0])

    ## Breathing
    def breathingAddFunc(self):
        color = "#" + picker.pick("Color").lower()
        actual, closest = get_colour_name(webcolors.hex_to_rgb(color))
        if not actual:
            actual = closest
        self.breathingList.addItem(QListWidgetItem(actual + "(" + color + ")"))

    def breathingDeleteFunc(self):
        self.breathingList.takeItem(self.breathingList.currentRow())

    def breathingApply(self):
        with serial.Serial(self.portTxt.text(), 256000) as ser:
            if self.getChannel() == None:
                hue.power(ser, 0, "off")
            else:
                speed = self.breathingSpeed.value()
                hue.breathing(ser, 0, self.getChannel(), self.getColors(self.breathingList), speed)

    ## Fading
    def fadingAddFunc(self):
        color = "#" + picker.pick("Color").lower()
        actual, closest = get_colour_name(webcolors.hex_to_rgb(color))
        if not actual:
            actual = closest
        self.fadingList.addItem(QListWidgetItem(actual + "(" + color + ")"))

    def fadingDeleteFunc(self):
        self.fadingList.takeItem(self.fadingList.currentRow())

    def fadingApply(self):
        with serial.Serial(self.portTxt.text(), 256000) as ser:
            if self.getChannel() == None:
                hue.power(ser, 0, "off")
            else:
                speed = self.fadingSpeed.value()
                hue.fading(ser, 0, self.getChannel(), self.getColors(self.fadingList), speed)

    ## Marquee
    def marqueeAddFunc(self):
        if self.marqueeList.count() == 1:
            self.error("Marquee cannot have more than one color")
        else:
            color = "#" + picker.pick("Color").lower()
            actual, closest = get_colour_name(webcolors.hex_to_rgb(color))
            if not actual:
                actual = closest
            self.marqueeList.addItem(QListWidgetItem(actual + "(" + color + ")"))

    def marqueeDeleteFunc(self):
        self.marqueeList.takeItem(self.marqueeList.currentRow())

    def marqueeApply(self):
        with serial.Serial(self.portTxt.text(), 256000) as ser:
            if self.getChannel() == None:
                hue.power(ser, 0, "off")
            else:
                print(self.getChannel())
                speed = self.marqueeSpeed.value()
                size = self.marqueeSize.value()
                direction = 0 if self.marqueeBackwards.isChecked() else 0
                hue.marquee(ser, 0, self.getChannel(), self.getColors(self.marqueeList)[0], speed, size, direction)

    ## coverMarquee
    def coverMarqueeAddFunc(self):
        color = "#" + picker.pick("Color").lower()
        actual, closest = get_colour_name(webcolors.hex_to_rgb(color))
        if not actual:
            actual = closest
        self.coverMarqueeList.addItem(QListWidgetItem(actual + "(" + color + ")"))

    def coverMarqueeDeleteFunc(self):
        self.coverMarqueeList.takeItem(self.coverMarqueeList.currentRow())

    def coverMarqueeApply(self):
        with serial.Serial(self.portTxt.text(), 256000) as ser:
            if self.getChannel() == None:
                hue.power(ser, 0, "off")
            else:
                speed = self.coverMarqueeSpeed.value()
                direction = 0 if self.coverMarqueeBackwards.isChecked() else 0
                hue.cover_marquee(ser, 0, self.getChannel(), self.getColors(self.coverMarqueeList), speed, direction)

    ## pulse
    def pulseAddFunc(self):
        color = "#" + picker.pick("Color").lower()
        actual, closest = get_colour_name(webcolors.hex_to_rgb(color))
        if not actual:
            actual = closest
        self.pulseList.addItem(QListWidgetItem(actual + "(" + color + ")"))

    def pulseDeleteFunc(self):
        self.pulseList.takeItem(self.pulseList.currentRow())

    def pulseApply(self):
        with serial.Serial(self.portTxt.text(), 256000) as ser:
            if self.getChannel() == None:
                hue.power(ser, 0, "off")
            else:
                speed = self.pulseSpeed.value()
                hue.pulse(ser, 0, self.getChannel(), self.getColors(self.pulseList), speed)

    ## spectrum
    def spectrumApply(self):
        with serial.Serial(self.portTxt.text(), 256000) as ser:
            if self.getChannel() == None:
                hue.power(ser, 0, "off")
            else:
                speed = self.spectrumSpeed.value()
                direction = 1 if self.spectrumBackwards.isChecked() else 0
                hue.spectrum(ser, self.getChannel(), speed, direction)

    ## alternating
    def alternatingAddFunc(self):
        if self.alternatingList.count() == 2:
            self.error("Alternating cannot have more than two colors")
        else:
            color = "#" + picker.pick("Color").lower()
            actual, closest = get_colour_name(webcolors.hex_to_rgb(color))
            if not actual:
                actual = closest
            self.alternatingList.addItem(QListWidgetItem(actual + "(" + color + ")"))

    def alternatingDeleteFunc(self):
        self.alternatingList.takeItem(self.alternatingList.currentRow())

    def alternatingApply(self):
        if self.alternatingList.count() != 2:
            self.error("Alternating must have two colors")
        else:
            with serial.Serial(self.portTxt.text(), 256000) as ser:
                if self.getChannel() == None:
                    hue.power(ser, 0, "off")
                else:
                    speed = self.alternatingSpeed.value()
                    size = self.alternatingSize.value()
                    direction = 1 if self.alternatingBackwards.isChecked() else 0
                    moving = self.alternatingMoving.isChecked()
                    hue.alternating(ser, 0, self.getChannel(), self.getColors(self.alternatingList), speed, size, moving, direction)

    ## candle
    def candleAddFunc(self):
        if self.candleList.count() == 1:
            self.error("Candle cannot have more than 1 color")
        else:
            color = "#" + picker.pick("Color").lower()
            actual, closest = get_colour_name(webcolors.hex_to_rgb(color))
            if not actual:
                actual = closest
            self.candleList.addItem(QListWidgetItem(actual + "(" + color + ")"))

    def candleDeleteFunc(self):
        self.candleList.takeItem(self.candleList.currentRow())

    def candleApply(self):
        with serial.Serial(self.portTxt.text(), 256000) as ser:
            if self.getChannel() == None:
                hue.power(ser, 0, "off")
            else:
                hue.candlelight(ser, 0, self.getChannel(), self.getColors(self.candleList)[0])

    ## wings
    def wingsAddFunc(self):
        if self.wingsList.count() == 1:
            self.error("Wings cannot have more than 1 color")
        else:
            color = "#" + picker.pick("Color").lower()
            actual, closest = get_colour_name(webcolors.hex_to_rgb(color))
            if not actual:
                actual = closest
            self.wingsList.addItem(QListWidgetItem(actual + "(" + color + ")"))

    def wingsDeleteFunc(self):
        self.wingsList.takeItem(self.wingsList.currentRow())

    def wingsApply(self):
        with serial.Serial(self.portTxt.text(), 256000) as ser:
            if self.getChannel() == None:
                hue.power(ser, 0, "off")
            else:
                speed = self.wingsSpeed.value()
                hue.wings(ser, 0, self.getChannel(), self.getColors(self.wingsList)[0], speed)

    ## audio_level
    def audioLevelAddFunc(self):
        color = "#" + picker.pick("Color").lower()
        actual, closest = get_colour_name(webcolors.hex_to_rgb(color))
        if not actual:
            actual = closest
        self.audioLevelList.addItem(QListWidgetItem(actual + "(" + color + ")"))

    def audioLevelDeleteFunc(self):
        self.audioLevelList.takeItem(self.audioLevelList.currentRow())

    def audioLevelApply(self):
        with serial.Serial(self.portTxt.text(), 256000) as ser:
            if self.getChannel() == None:
                hue.power(ser, 0, "off")
            else:
                tolerance = float(self.audioLevelTolerance.value())
                smooth = int(self.audioLevelTolerance.value())
                hue.audio_level(ser, 0, self.getChannel(), self.getColors(self.audioLevelList), tolerance, smooth)


    def applyFunc(self):
        self.indexApply[self.presetModeWidget.currentIndex()]()

if __name__ == '__main__':
    #if os.geteuid() != 0:
    #    sys.exit("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'.")
    app = QApplication(sys.argv)
    form = MainWindow()
    form.show()
    sys.exit(app.exec_())
