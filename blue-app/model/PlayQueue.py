from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

class PlayQueue(QtCore.QAbstractTableModel):

    playQueueEmpty = QtCore.pyqtSignal()
    playQueueNotEmpty = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.queue = []
    def isEmpty(self):
        return len(self.queue) == 0

    def popFromPlayQueue(self):
        self.beginRemoveRows(QtCore.QModelIndex(), 0, 0)
        val = self.queue[0]
        del self.queue[0]
        self.endRemoveRows()
        if self.isEmpty():
            self.playQueueEmpty.emit()
        return val 

    def addToPlayQueue(self, mp3info):
        position = len(self.queue)
        self.beginInsertRows(QtCore.QModelIndex(), position, position)
        self.queue.append(mp3info)
        self.endInsertRows()
        if self.rowCount() == 1:
            self.playQueueNotEmpty.emit()

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.queue)

    def columnCount(self, parent=QtCore.QModelIndex()):
        #return 2
        return 1

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            if index.column() == 0:
                return self.queue[index.row()][0]
            else:
                return self.queue[index.row()][2] 
        else:
            return QtCore.QVariant()

