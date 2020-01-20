from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

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

    def addToPlayQueue(self, mp3info):
        position = len(self.queue)
        self.queue.append(mp3info)
        if self.rowCount() == 1:
            self.playQueueNotEmpty.emit()
        self.playQueueAdded.emit()

    def rowCount(self):
        return len(self.queue)
    
    def data(self, index):
        return self.queue[index]

