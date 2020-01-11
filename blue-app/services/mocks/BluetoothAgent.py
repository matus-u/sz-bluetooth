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
        self.connected.emit(1)
        pass

    def disconnect(self):
        pass
