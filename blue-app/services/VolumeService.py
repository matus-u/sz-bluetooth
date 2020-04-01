from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

import orangepi.pc
import OPi.GPIO as GPIO
import os

from services import TimerService

class VolumeService(TimerService.TimerStatusObject):

    signalVolumeUp = QtCore.pyqtSignal()
    signalVolumeDown = QtCore.pyqtSignal()
    signalMute = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__(150)
        GPIO.setmode(orangepi.pc.BOARD)

        GPIO.setup(27, GPIO.IN)
        GPIO.add_event_detect(27, GPIO.RISING, callback=self.volumeMute)

        self.GPIO_CONFIG = { 21 : self.volumeDown, 22 : self.volumeUp }
        for num in self.GPIO_CONFIG:
            GPIO.setup(num, GPIO.IN)

        self.active = True

    def testModeDisabled(self):
        self.active = True

    def testModeEnabled(self):
        self.active = False

    def onTimeout(self):
        for num,callback in self.GPIO_CONFIG.items():
            if GPIO.input(num) == GPIO.HIGH:
                callback()

    def volumeMute(self, channel):
        if self.active:
            os.system("amixer sset 'Line Out' toggle")
        self.signalMute.emit()

    def volumeUp(self):
        if self.active:
            os.system("amixer sset 'Line Out' 1%+")
        self.signalVolumeUp.emit()

    def volumeDown(self):
        if self.active:
            os.system("amixer sset 'Line Out' 1%-")
        self.signalVolumeDown.emit()
