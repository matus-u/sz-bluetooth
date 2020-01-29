from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

class Agent():
    def __init__(self):
        pass

class PairRequest(QtCore.QObject):
    connected = QtCore.pyqtSignal(int)


    def __init__(self):
        super().__init__()

    def pair(self, deviceAddress):
        QtCore.QTimer.singleShot(5000, self.end)
        pass

    def end(self):
        self.connected.emit(0)

    def disconnect(self):
        pass
