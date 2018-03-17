#!/usr/bin/env python3
VERSION="1.4.5"
import sys
import io
import traceback
from time import sleep
import os
import types
import functools
import ctypes
import urllib.request
import multiprocessing
import queue
import datetime
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QGridLayout, QLabel, QLineEdit, QMessageBox, QColorDialog
from PyQt5.QtWidgets import QTextEdit, QWidget, QMainWindow, QApplication, QListWidgetItem, QTableWidgetItem

package_import = True
if package_import:
    from . import hue_gui 
    from . import hue
    from . import previous
    from . import webcolors
else:
    import hue_gui
    import hue
    import previous
    import webcolors
#from . import hue_gui # REMEMBER TO CHANGE BACK
#from . import hue

import serial
from serial.tools import list_ports


def is_admin():
    if os.name == 'nt':
        # WARNING: requires Windows XP SP2 or higher!
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    else:
        return True

def runAsAdmin():

    if os.name != 'nt':
        return
    else:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, "", None, 1)

def main():
    #if os.geteuid() != 0:
    #    sys.exit("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'.")
    #if not is_admin():
    #    runAsAdmin()
    sys.excepthook = excepthook
    app = QApplication(sys.argv)
    form = MainWindow()
    form.show()
    sys.exit(app.exec_())

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

def pick(n):
    c = QColorDialog.getColor()
    if c.isValid():
        return c.name()[1:].upper()

def versiontuple(v):
    return tuple(map(int, (v.split("."))))

def time_in_range(start, end, x):
    """Return true if x is in the range [start, end]"""
    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end

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
            10: self.audioLevelApply,
            11: self.customApply,
            12: self.profileApply,
            13: self.animatedApply
            }

        self.animatedColors = []

        self.unitLEDBtn.clicked.connect(self.toggleUnitLED)

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
        self.customEdit.clicked.connect(self.customEditFunc)
        self.profileAdd.clicked.connect(self.profileAddFunc)
        self.profileDelete.clicked.connect(self.profileDeleteFunc)
        self.profileRefresh.clicked.connect(self.profileListFunc)
        self.animatedAdd.clicked.connect(self.animatedAddFunc)
        self.animatedDelete.clicked.connect(self.animatedDeleteFunc)
        self.animatedEdit.clicked.connect(self.animatedEditFunc)
        self.animatedList.itemSelectionChanged.connect(self.animatedRoundChangeFunc)
        self.applyBtn.clicked.connect(self.applyFunc)

        self.timeSave.clicked.connect(self.timeSaveFunc)

        self.populateCustom()
        self.populateAnimated()

        if os.name == 'nt':
            self.portTxt.setText('COM3')
        self.update()
        port = self.get_port()
        if port:
            self.portTxt.setText(self.get_port())

        self.profileListFunc()

        try:
            with serial.Serial(self.portTxt.text(), 256000) as ser:
                hue.write_previous(ser)
        except serial.serialutil.SerialException:
            self.error("Serial port is invalid. Try /dev/ttyACM0 for Linux or COM3 or COM4 for Windows")

        times = previous.get_times()
        self.offTime.setText(times[0])
        self.onTime.setText(times[1])
        self.offTimeTxt = times[0]
        self.onTimeTxt = times[1]

        self.doneOff = False
        self.doneOn = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.timeDaemon)
        self.timer.start(1000*60)

        self.audioThread = None
        self.animatedThread = None

        self.unitLED = 'on'

    def closeEvent(self, event):
        self.checkAudio()
        event.accept()

    def error(self, message):
        msg = QMessageBox()
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.Ok)
        out = msg.exec_()

    def get_port(self):
        ports = []
        for port in list_ports.comports():
            if 'MCP2200' in port[1] or 'USB Serial Device' in port[1] or 'USB Serial Port' in port[1]:
                ports.append(port[0])
        if ports:
            return ports[0]
        else:
            return None

    def checkAudio(self):
        if self.audioThread:
            if self.audioThread.is_alive():
                self.audioThread.terminate()
                sleep(0.1)
        if self.animatedThread:
            if self.animatedThread.is_alive():
                self.animatedThread.terminate()
                sleep(0.1)

    def update(self):
        with urllib.request.urlopen('https://raw.githubusercontent.com/kusti8/hue-plus/master/version') as response:
            version_new = response.read().strip()
            if versiontuple(version_new.decode()) > versiontuple(VERSION):
                self.error("There is a new update available. Download it from https://github.com/kusti8/hue-plus")

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

    def toggleUnitLED(self):
        if self.unitLED == 'on':
            self.unitLED = 'off'
        else:
            self.unitLED = 'on'

        with serial.Serial(self.portTxt.text(), 256000) as ser:
            hue.unitled(ser, self.unitLED)

    def timeDaemon(self):
        pre = previous.list_profile()
        if 'previous' in pre:
            pre = 'previous'
        else:
            return
        if self.onTimeTxt != "00:00" and self.offTimeTxt != "00:00":
            onTime = datetime.datetime.strptime(self.onTimeTxt, '%H:%M').time()
            offTime = datetime.datetime.strptime(self.offTimeTxt, '%H:%M').time()


            if time_in_range(offTime, onTime, datetime.datetime.now().time()):
                if not self.doneOff:
                    self.checkAudio()
                    try:
                        with serial.Serial(self.portTxt.text(), 256000) as ser:
                            print("Turning off")
                            hue.power(ser, 0, 'off')
                            hue.unitled(ser, 'off')
                            self.doneOff = True
                            self.doneOn = False
                    except serial.serialutil.SerialException:
                        self.error("Serial port is invalid. Try /dev/ttyACM0 for Linux or COM3 or COM4 for Windows")
            else:
                if not self.doneOn:
                    self.checkAudio()
                    try:
                        with serial.Serial(self.portTxt.text(), 256000) as ser:
                            print("Turning on")
                            hue.profile_apply(ser, pre)
                            hue.unitled(ser, 'on')
                            self.doneOn = True
                            self.doneOff = False
                    except serial.serialutil.SerialException:
                        self.error("Serial port is invalid. Try /dev/ttyACM0 for Linux or COM3 or COM4 for Windows")

    ## Time
    def timeSaveFunc(self):
        self.onTimeTxt = self.onTime.text()
        self.offTimeTxt = self.offTime.text()
        previous.apply_times([self.offTimeTxt, self.onTimeTxt])

    ## Fixed
    def fixedAddFunc(self):
        if self.fixedList.count() == 1:
            self.error("Fixed cannot have more than one color")
        else:
            hex_color = pick("Color")
            if hex_color is None:
                return
            color = "#" + hex_color.lower()
            actual, closest = get_colour_name(webcolors.hex_to_rgb(color))
            if not actual:
                actual = closest
            self.fixedList.addItem(QListWidgetItem(actual + "(" + color + ")"))

    def fixedDeleteFunc(self):
        self.fixedList.takeItem(self.fixedList.currentRow())

    def fixedApply(self):
        self.checkAudio()
        try:
            with serial.Serial(self.portTxt.text(), 256000) as ser:
                print("Applying")
                if self.getChannel() == None:
                    hue.power(ser, 0, "off")
                else:
                    hue.fixed(ser, 0, self.getChannel(), self.getColors(self.fixedList)[0])
        except serial.serialutil.SerialException:
            self.error("Serial port is invalid. Try /dev/ttyACM0 for Linux or COM3 or COM4 for Windows")

    ## Breathing
    def breathingAddFunc(self):
        color = "#" + pick("Color").lower()
        actual, closest = get_colour_name(webcolors.hex_to_rgb(color))
        if not actual:
            actual = closest
        self.breathingList.addItem(QListWidgetItem(actual + "(" + color + ")"))

    def breathingDeleteFunc(self):
        self.breathingList.takeItem(self.breathingList.currentRow())

    def breathingApply(self):
        self.checkAudio()
        try:
            with serial.Serial(self.portTxt.text(), 256000) as ser:
                if self.getChannel() == None:
                    hue.power(ser, 0, "off")
                else:
                    speed = self.breathingSpeed.value()
                    hue.breathing(ser, 0, self.getChannel(), self.getColors(self.breathingList), speed)
        except serial.serialutil.SerialException:
            self.error("Serial port is invalid. Try /dev/ttyACM0 for Linux or COM3 or COM4 for Windows")

    ## Fading
    def fadingAddFunc(self):
        hex_color = pick("Color")
        if hex_color is None:
            return
        color = "#" + hex_color.lower()
        actual, closest = get_colour_name(webcolors.hex_to_rgb(color))
        if not actual:
            actual = closest
        self.fadingList.addItem(QListWidgetItem(actual + "(" + color + ")"))

    def fadingDeleteFunc(self):
        self.fadingList.takeItem(self.fadingList.currentRow())

    def fadingApply(self):
        self.checkAudio()
        try:
            with serial.Serial(self.portTxt.text(), 256000) as ser:
                if self.getChannel() == None:
                    hue.power(ser, 0, "off")
                else:
                    speed = self.fadingSpeed.value()
                    hue.fading(ser, 0, self.getChannel(), self.getColors(self.fadingList), speed)
        except serial.serialutil.SerialException:
            self.error("Serial port is invalid. Try /dev/ttyACM0 for Linux or COM3 or COM4 for Windows")

    ## Marquee
    def marqueeAddFunc(self):
        if self.marqueeList.count() == 1:
            self.error("Marquee cannot have more than one color")
        else:
            hex_color = pick("Color")
            if hex_color is None:
                return
            color = "#" + hex_color.lower()
            actual, closest = get_colour_name(webcolors.hex_to_rgb(color))
            if not actual:
                actual = closest
            self.marqueeList.addItem(QListWidgetItem(actual + "(" + color + ")"))

    def marqueeDeleteFunc(self):
        self.marqueeList.takeItem(self.marqueeList.currentRow())

    def marqueeApply(self):
        self.checkAudio()
        try:
            with serial.Serial(self.portTxt.text(), 256000) as ser:
                if self.getChannel() == None:
                    hue.power(ser, 0, "off")
                else:
                    speed = self.marqueeSpeed.value()
                    size = self.marqueeSize.value()
                    direction = 0 if self.marqueeBackwards.isChecked() else 0
                    hue.marquee(ser, 0, self.getChannel(), self.getColors(self.marqueeList)[0], speed, size, direction)
        except serial.serialutil.SerialException:
            self.error("Serial port is invalid. Try /dev/ttyACM0 for Linux or COM3 or COM4 for Windows")

    ## coverMarquee
    def coverMarqueeAddFunc(self):
        hex_color = pick("Color")
        if hex_color is None:
            return
        color = "#" + hex_color.lower()
        actual, closest = get_colour_name(webcolors.hex_to_rgb(color))
        if not actual:
            actual = closest
        self.coverMarqueeList.addItem(QListWidgetItem(actual + "(" + color + ")"))

    def coverMarqueeDeleteFunc(self):
        self.coverMarqueeList.takeItem(self.coverMarqueeList.currentRow())

    def coverMarqueeApply(self):
        self.checkAudio()
        try:
            with serial.Serial(self.portTxt.text(), 256000) as ser:
                if self.getChannel() == None:
                    hue.power(ser, 0, "off")
                else:
                    speed = self.coverMarqueeSpeed.value()
                    direction = 0 if self.coverMarqueeBackwards.isChecked() else 0
                    hue.cover_marquee(ser, 0, self.getChannel(), self.getColors(self.coverMarqueeList), speed, direction)
        except serial.serialutil.SerialException:
            self.error("Serial port is invalid. Try /dev/ttyACM0 for Linux or COM3 or COM4 for Windows")

    ## pulse
    def pulseAddFunc(self):
        color = "#" + pick("Color").lower()
        actual, closest = get_colour_name(webcolors.hex_to_rgb(color))
        if not actual:
            actual = closest
        self.pulseList.addItem(QListWidgetItem(actual + "(" + color + ")"))

    def pulseDeleteFunc(self):
        self.pulseList.takeItem(self.pulseList.currentRow())

    def pulseApply(self):
        self.checkAudio()
        try:
            with serial.Serial(self.portTxt.text(), 256000) as ser:
                if self.getChannel() == None:
                    hue.power(ser, 0, "off")
                else:
                    speed = self.pulseSpeed.value()
                    hue.pulse(ser, 0, self.getChannel(), self.getColors(self.pulseList), speed)
        except serial.serialutil.SerialException:
            self.error("Serial port is invalid. Try /dev/ttyACM0 for Linux or COM3 or COM4 for Windows")

    ## spectrum
    def spectrumApply(self):
        self.checkAudio()
        try:
            with serial.Serial(self.portTxt.text(), 256000) as ser:
                if self.getChannel() == None:
                    hue.power(ser, 0, "off")
                else:
                    speed = self.spectrumSpeed.value()
                    direction = 1 if self.spectrumBackwards.isChecked() else 0
                    hue.spectrum(ser, self.getChannel(), speed, direction)
        except serial.serialutil.SerialException:
            self.error("Serial port is invalid. Try /dev/ttyACM0 for Linux or COM3 or COM4 for Windows")

    ## alternating
    def alternatingAddFunc(self):
        if self.alternatingList.count() == 2:
            self.error("Alternating cannot have more than two colors")
        else:
            hex_color = pick("Color")
            if hex_color is None:
                return
            color = "#" + hex_color.lower()
            actual, closest = get_colour_name(webcolors.hex_to_rgb(color))
            if not actual:
                actual = closest
            self.alternatingList.addItem(QListWidgetItem(actual + "(" + color + ")"))

    def alternatingDeleteFunc(self):
        self.alternatingList.takeItem(self.alternatingList.currentRow())

    def alternatingApply(self):
        self.checkAudio()
        try:
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
        except serial.serialutil.SerialException:
            self.error("Serial port is invalid. Try /dev/ttyACM0 for Linux or COM3 or COM4 for Windows")
    ## candle
    def candleAddFunc(self):
        if self.candleList.count() == 1:
            self.error("Candle cannot have more than 1 color")
        else:
            hex_color = pick("Color")
            if hex_color is None:
                return
            color = "#" + hex_color.lower()
            actual, closest = get_colour_name(webcolors.hex_to_rgb(color))
            if not actual:
                actual = closest
            self.candleList.addItem(QListWidgetItem(actual + "(" + color + ")"))

    def candleDeleteFunc(self):
        self.candleList.takeItem(self.candleList.currentRow())

    def candleApply(self):
        self.checkAudio()
        try:
            with serial.Serial(self.portTxt.text(), 256000) as ser:
                if self.getChannel() == None:
                    hue.power(ser, 0, "off")
                else:
                    hue.candlelight(ser, 0, self.getChannel(), self.getColors(self.candleList)[0])
        except serial.serialutil.SerialException:
            self.error("Serial port is invalid. Try /dev/ttyACM0 for Linux or COM3 or COM4 for Windows")

    ## wings
    def wingsAddFunc(self):
        if self.wingsList.count() == 1:
            self.error("Wings cannot have more than 1 color")
        else:
            hex_color = pick("Color")
            if hex_color is None:
                return
            color = "#" + hex_color.lower()
            actual, closest = get_colour_name(webcolors.hex_to_rgb(color))
            if not actual:
                actual = closest
            self.wingsList.addItem(QListWidgetItem(actual + "(" + color + ")"))

    def wingsDeleteFunc(self):
        self.wingsList.takeItem(self.wingsList.currentRow())

    def wingsApply(self):
        self.checkAudio()
        try:
            with serial.Serial(self.portTxt.text(), 256000) as ser:
                if self.getChannel() == None:
                    hue.power(ser, 0, "off")
                else:
                    speed = self.wingsSpeed.value()
                    hue.wings(ser, 0, self.getChannel(), self.getColors(self.wingsList)[0], speed)
        except serial.serialutil.SerialException:
            self.error("Serial port is invalid. Try /dev/ttyACM0 for Linux or COM3 or COM4 for Windows")

    ## audio_level
    def audioLevelAddFunc(self):
        hex_color = pick("Color")
        if hex_color is None:
            return
        color = "#" + hex_color.lower()
        actual, closest = get_colour_name(webcolors.hex_to_rgb(color))
        if not actual:
            actual = closest
        self.audioLevelList.addItem(QListWidgetItem(actual + "(" + color + ")"))

    def audioLevelDeleteFunc(self):
        self.audioLevelList.takeItem(self.audioLevelList.currentRow())

    def audioLevelApply(self):
        if os.name == 'nt':
            self.error("To enable audio mode on Windows, right click on the audio icon, go to recording devices, right click and select show disabled devices, and right click on stereo mix and click enable.")
        self.checkAudio()
        try:
            ser = serial.Serial(self.portTxt.text(), 256000)
            if self.getChannel() == None:
                hue.power(ser, 0, "off")
            else:
                tolerance = float(self.audioLevelTolerance.value())
                smooth = int(self.audioLevelSmooth.value())
                self.audioThread = multiprocessing.Process(target=hue.audio_level, args=(self.portTxt.text(), 0, self.getChannel(), self.getColors(self.audioLevelList), tolerance, smooth))
                self.audioThread.start()
        except serial.serialutil.SerialException:
            self.error("Serial port is invalid. Try /dev/ttyACM0 for Linux or COM3 or COM4 for Windows")

    ## profile
    def profileAddFunc(self):
        if self.animatedThread:
            if self.animatedThread.is_alive():
                previous.write(customs={'name': self.profileName.text(),'colors': self.animatedColors, 'speed': self.animatedSpeed.value()})
            else:
                hue.profile_add(self.profileName.text())
        else:
            hue.profile_add(self.profileName.text())
        self.profileList.addItem(QListWidgetItem(self.profileName.text()))

    def profileDeleteFunc(self):
        hue.profile_rm(self.profileList.currentItem().text())
        self.audioLevelList.takeItem(self.profileList.currentRow())
        self.profileListFunc()

    def profileApply(self):
        self.checkAudio()
        try:
            with serial.Serial(self.portTxt.text(), 256000) as ser:
                if self.getChannel() == None:
                    hue.power(ser, 0, "off")
                else:
                    out = hue.profile_apply(ser, self.profileList.currentItem().text())
        except serial.serialutil.SerialException:
            self.error("Serial port is invalid. Try /dev/ttyACM0 for Linux or COM3 or COM4 for Windows")
        
        if out:
            self.animatedColors = out['colors']
            self.animatedSpeed.setValue(out['speed'])
            self.animatedApply()

    def profileListFunc(self):
        self.profileList.clear()
        profiles = previous.list_profile()
        if profiles:
            for p in profiles:
                self.profileList.addItem(QListWidgetItem(p))

    def applyFunc(self):
        self.indexApply[self.presetModeWidget.currentIndex()]()

    # custom
    def populateCustom(self):
        actual, closest = get_colour_name(webcolors.hex_to_rgb('#FFFFFF'))
        if not actual:
            actual = closest
        for i in range(40):
            self.customTable.setItem(i, 0, QTableWidgetItem(str(i+1)))
            self.customTable.setItem(i, 1, QTableWidgetItem(actual + '(#FFFFFF)'))

    def customEditFunc(self):
        hex_color = pick("Color")
        if hex_color is None:
            return
        color = "#" + hex_color.lower()
        actual, closest = get_colour_name(webcolors.hex_to_rgb(color))
        if not actual:
            actual = closest
        
        for widgetItem in self.customTable.selectedItems():
            if widgetItem.column() != 0:
                widgetItem.setText(actual + "(" + color + ")")
                widgetItem.setBackground(QColor(*webcolors.hex_to_rgb(color)))

    def customGetColors(self):
        colors = []
        for i in range(40):
            colors.append(find_between(self.customTable.item(i, 1).text(), '#', ')').upper())
        return colors

    def customApply(self):
        self.checkAudio()
        try:
            with serial.Serial(self.portTxt.text(), 256000) as ser:
                if self.getChannel() == None:
                    hue.power(ser, 0, "off")
                else:
                    speed = self.customSpeed.value()
                    hue.custom(ser, 0, self.getChannel(), self.customGetColors(), self.customMode.currentText().lower(), speed)
        except serial.serialutil.SerialException:
            self.error("Serial port is invalid. Try /dev/ttyACM0 for Linux or COM3 or COM4 for Windows")

    # Animated
    def populateAnimated(self):
        actual, closest = get_colour_name(webcolors.hex_to_rgb('#FFFFFF'))
        if not actual:
            actual = closest
        for i in range(40):
            self.animatedTable.setItem(i, 0, QTableWidgetItem(str(i+1)))
            self.animatedTable.setItem(i, 1, QTableWidgetItem(actual + '(#FFFFFF)'))

    def populateAnimatedColors(self, colors):
        for index, i in enumerate(colors):
            actual, closest = get_colour_name(webcolors.hex_to_rgb('#' + i))
            if not actual:
                actual = closest
            self.animatedTable.setItem(index, 0, QTableWidgetItem(str(index+1)))
            self.animatedTable.setItem(index, 1, QTableWidgetItem(actual + '(#' + i + ')'))
            self.animatedTable.item(index, 1).setBackground(QColor(*webcolors.hex_to_rgb('#' + i)))

    def animatedEditFunc(self):
        hex_color = pick("Color")
        if hex_color is None:
            return
        color = "#" + hex_color.lower()
        actual, closest = get_colour_name(webcolors.hex_to_rgb(color))
        if not actual:
            actual = closest
        
        for widgetItem in self.animatedTable.selectedItems():
            if widgetItem.column() != 0:
                widgetItem.setText(actual + "(" + color + ")")
                widgetItem.setBackground(QColor(*webcolors.hex_to_rgb(color)))
                if self.animatedList.currentRow() != -1:
                    self.animatedColors[self.animatedList.currentRow()][widgetItem.row()] = color[1:]

    def animatedGetColors(self):
        colors = []
        for i in range(40):
            colors.append(find_between(self.animatedTable.item(i, 1).text(), '#', ')').upper())
        return colors

    def animatedAddFunc(self):
        self.animatedList.addItem(QListWidgetItem(self.animatedRoundName.text()))
        self.animatedColors.append(['FFFFFF'] * 40)

    def animatedDeleteFunc(self):
        self.animatedList.takeItem(self.animatedList.currentRow())
        self.animatedColors.pop(self.animatedList.currentRow())

    def animatedRoundChangeFunc(self):
        self.populateAnimatedColors(self.animatedColors[self.animatedList.currentRow()])

    def animatedApply(self):
        self.checkAudio()
        self.animatedThread = multiprocessing.Process(target=hue.animated, args=(self.portTxt.text(), self.getChannel(), self.animatedColors, self.animatedSpeed.value()))
        self.animatedThread.start()


def excepthook(excType, excValue, tracebackobj):
    """Rewritten "excepthook" function, to display a message box with details about the exception.
    @param excType exception type
    @param excValue exception value
    @param tracebackobj traceback object
    """
    separator = '-' * 40
    notice = "An unhandled exception has occurred\n"

    tbinfofile = io.StringIO()
    traceback.print_tb(tracebackobj, None, tbinfofile)
    tbinfofile.seek(0)
    tbinfo = tbinfofile.read()
    errmsg = '%s: \n%s' % (str(excType), str(excValue))
    sections = [separator, errmsg, separator, tbinfo]
    msg = '\n'.join(sections)

    # Create a QMessagebox
    error_box = QMessageBox()

    error_box.setText(str(notice)+str(msg))
    error_box.setWindowTitle("Hue-plus - unhandled exception")
    error_box.setIcon(QMessageBox.Critical)
    error_box.setStandardButtons(QMessageBox.Ok)
    error_box.setTextInteractionFlags(Qt.TextSelectableByMouse)

    # Show the window
    error_box.exec_()
    sys.exit(1)

if __name__ == '__main__':
    main()
