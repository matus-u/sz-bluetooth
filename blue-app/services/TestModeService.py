from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

from services.LoggingService import LoggingService

class TestModeService(QtCore.QObject):
    testModeEnabled = QtCore.pyqtSignal()
    testModeDisabled = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()

    def enableTestMode(self):
        LoggingService.getLogger().info("Test mode enabled.")
        self.testModeEnabled.emit()

    def disableTestMode(self):
        LoggingService.getLogger().info("Test mode disabled.")
        self.testModeDisabled.emit()
