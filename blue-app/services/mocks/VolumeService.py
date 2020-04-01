from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

import os
from services import TimerService

class VolumeService(TimerService.TimerStatusObject):

    signalVolumeUp = QtCore.pyqtSignal()
    signalVolumeDown = QtCore.pyqtSignal()
    signalMute = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__(150)

    def onTimeout(self):
        pass

    def volumeMute(self, channel):
        self.signalMute.emit()

    def volumeUp(self):
        self.signalVolumeUp.emit()

    def volumeDown(self):
        self.signalVolumeDown.emit()

    def cleanup(self):
        pass

    def testModeEnabled(self):
        print ("Test mode in volume enabled")

    def testModeDisabled(self):
        print ("Test mode in volume disabled")
