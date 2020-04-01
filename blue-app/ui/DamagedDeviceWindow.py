from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from generated.DamagedDevice import Ui_DamagedDevice

class DamagedDeviceWindow(QtWidgets.QDialog):
    def __init__(self, parent, message, info):
        super(DamagedDeviceWindow, self).__init__(parent)

        self.ui = Ui_DamagedDevice()
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.ui.setupUi(self)
        self.ui.hwErrorLabel.setText(message + " " + info)
