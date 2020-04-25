from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from generated.DamagedDevice import Ui_DamagedDevice

class DamagedDeviceWindow(QtWidgets.QDialog):

    hidden = QtCore.pyqtSignal()

    def __init__(self, parent, hwErrorHandler):
        super(DamagedDeviceWindow, self).__init__(parent)

        hwErrorHandler.hwErrorChanged.connect(lambda errors: self.onHwErrorChanged(errors, parent))

        self.ui = Ui_DamagedDevice()
        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.ui.setupUi(self)

    def onHwErrorChanged(self, errors, parent):
        self.ui.damagedDeviceText.clear()

        if len(errors) == 0:
            self.hide()
            self.hidden.emit()

        if len(errors) > 0:
            text = ""
            for i in errors:
                text += str(i + "\n")

            self.ui.damagedDeviceText.insertPlainText(text)
            self.show()
            self.raise_()
            self.activateWindow()

            self.move(self.pos().x(), parent.pos().y() + 60)

