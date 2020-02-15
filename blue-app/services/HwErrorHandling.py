from PyQt5 import QtCore

class HwErrorHandling(QtCore.QObject):
    hwError = QtCore.pyqtSignal(str, str)

    def __init__(self):
        super().__init__()

    def hwErrorEmit(self, info):
        self.hwError.emit(" HW ERROR!!!", info)

