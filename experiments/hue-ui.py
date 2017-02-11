import sys
sys.path.append('..')
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
            9: self.wingsApply}

        self.fixedAdd.clicked.connect(self.fixedAddFunc)
        self.fixedDelete.clicked.connect(self.fixedDeleteFunc)
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
        for i in range(modeList.count):
            colors.append(find_between(modeList.item(0).text, '#', ')').upper())
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
            if getChannel() == None:
                hue.power(ser, 0, "off")
            else:
                hue.fixed(ser, 0, getChannel(), self.getColors(self.fixedList)[0])

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
            if getChannel() == None:
                hue.power(ser, 0, "off")
            else:
                speed = self.breathingSpeed.value()
                hue.breathing(ser, 0, getChannel(), self.getColors(self.breathingList), speed)

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
            if getChannel() == None:
                hue.power(ser, 0, "off")
            else:
                speed = self.fadingSpeed.value()
                hue.fading(ser, 0, getChannel(), self.getColors(self.fadingList), speed)

    ## Marquee
    def marqueeAddFunc(self):
        color = "#" + picker.pick("Color").lower()
        actual, closest = get_colour_name(webcolors.hex_to_rgb(color))
        if not actual:
            actual = closest
        self.marqueeList.addItem(QListWidgetItem(actual + "(" + color + ")"))

    def fadingDeleteFunc(self):
        self.marqueeList.takeItem(self.marqueeList.currentRow())

    def fadingApply(self):
        with serial.Serial(self.portTxt.text(), 256000) as ser:
            if getChannel() == None:
                hue.power(ser, 0, "off")
            else:
                speed = self.marqueeSpeed.value()
                size = self.marqueeSize.value()
                direction = 1 if self.marqueeBackwards.isChecked() else 0
                hue.fading(ser, 0, getChannel(), self.getColors(self.fadingList), speed)

    def applyFunc(self):
        self.presetModeWidget.currentIndex()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = MainWindow()
    form.show()
    sys.exit(app.exec_())
