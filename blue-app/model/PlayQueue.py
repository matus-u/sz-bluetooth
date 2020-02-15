from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

from model.PlayQueueObject import Mp3PlayQueueObject, BluetoothPlayQueueObject

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

    def totalPlayQueueTime(self):
        return sum([x.duration() for x in self.queue])

    def getNextStartTime(self):
        if self.isEmpty():
            return None
        else:
            return self.queue[-1].endTime()
