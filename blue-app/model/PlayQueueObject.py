from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

from datetime import timedelta

class Mp3PlayQueueObject:
    def __init__(self, mp3Info):
        self.mp3info = mp3Info
        self._startTime = None

    def mp3Info(self):
        return self.mp3info

    def duration(self):
        return self.mp3info[2]

    def name(self):
        return self.mp3info[0]

    def path(self):
        return self.mp3info[1]

    def setStartTime(self, startTime):
        self._startTime = startTime

    def startTime(self):
        return self._startTime

    def endTime(self):
        return self._startTime + timedelta(seconds=self.duration())

    def genre(self):
        return self.mp3info[3]

class BluetoothPlayQueueObject:
    def __init__(self,  name, macAddr, duration):
        self._name = name
        self._macAddr = macAddr
        self._duration = duration
        self._startTime = None

    def duration(self):
        return self._duration

    def name(self):
        return self._name

    def macAddr(self):
        return self._macAddr

    def setStartTime(self, startTime):
        self._startTime = startTime

    def startTime(self):
        return self._startTime

    def endTime(self):
        return self._startTime + timedelta(seconds=self.duration())

    def getCount(self):
        return 0

    def path(self):
        return ""
