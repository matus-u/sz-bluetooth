from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

from datetime import timedelta

class LocalPlayQueueObject:
    def __init__(self, metadata):
        self._metadata = metadata
        self._startTime = None

    def isVideoSupported(self):
        return self._metadata[4]

    def metadata(self):
        return self._metadata

    def duration(self):
        return self._metadata[2]

    def name(self):
        return self._metadata[0]

    def path(self):
        return self._metadata[1]

    def setStartTime(self, startTime):
        self._startTime = startTime

    def startTime(self):
        return self._startTime

    def endTime(self):
        return self._startTime + timedelta(seconds=self.duration())

    def genre(self):
        return self._metadata[3]

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
