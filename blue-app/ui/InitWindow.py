from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from generated.Init import Ui_InitDevice

from services.LoggingService import LoggingService
import time

class InitWindow(QtWidgets.QDialog):

    appendSignal = QtCore.pyqtSignal(str)

    def __init__(self, parent):
        super(InitWindow, self).__init__(parent)

        self.ui = Ui_InitDevice()
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.ui.setupUi(self)
        self.appendSignal.connect(lambda text: self.appendText(text), QtCore.Qt.QueuedConnection)

    def appendTextThreadSafe(self, text):
        self.appendSignal.emit(text)

    def appendText(self, text):
        LoggingService.getLogger().info(text)
        self.ui.initDeviceText.appendPlainText(time.strftime("%H:%M:%S ", time.localtime()) + text)
