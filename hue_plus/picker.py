#!/usr/bin/env python3
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QColorDialog
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QColor

def pick(n):
    app = QApplication(sys.argv)

    w = QWidget()
    w.resize(250, 250)
    w.move(300, 300)
    w.setWindowTitle(n)
    w.show()
    c = QColorDialog.getColor()
    if c.isValid():
        return c.name()[1:].upper()
    sys.exit(app.exec_())
