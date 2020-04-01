from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

class TestModeService(QtCore.QObject):
    testModeEnabled = QtCore.pyqtSignal()
    testModeDisabled = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()

    def enableTestMode(self):
        self.testModeEnabled.emit()

    def disableTestMode(self):
        self.testModeDisabled.emit()
