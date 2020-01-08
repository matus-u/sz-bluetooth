from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

class GpioCallback(QtCore.QObject):
    callbackGpio = QtCore.pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)

    def onLowLevelCallback(self, channel):
        self.callbackGpio.emit()
