from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

class Mp3PlayQueueObject:
    def __init__(self, mp3Info):
        self.mp3info = mp3Info

    def duration(self):
        return self.mp3info[2]

    def name(self):
        return self.mp3info[0]

    def path(self):
        return self.mp3info[1]

class BluetoothPlayQueueObject:
    def __init__(self,  name, macAddr, duration):
        self._name = name
        self._macAddr = macAddr
        self._duration = duration

    def duration(self):
        return self._duration

    def name(self):
        return self._name

    def macAddr(self):
        return self._macAddr

class PlayQueue(QtCore.QAbstractTableModel):

    playQueueEmpty = QtCore.pyqtSignal()
    playQueueNotEmpty = QtCore.pyqtSignal()
    playQueueAdded = QtCore.pyqtSignal()
    playQueueRemoved = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.queue = []

    def isEmpty(self):
        return len(self.queue) == 0

    def popFromPlayQueue(self):
        val = self.queue[0]
        del self.queue[0]
        if self.isEmpty():
            self.playQueueEmpty.emit()
        self.playQueueRemoved.emit()
        return val 

    def addToPlayQueue(self, playQueueObject):
        position = len(self.queue)
        self.queue.append(playQueueObject)
        if self.rowCount() == 1:
            self.playQueueNotEmpty.emit()
        self.playQueueAdded.emit()

    def rowCount(self):
        return len(self.queue)
    
    def data(self, index):
        return self.queue[index]

