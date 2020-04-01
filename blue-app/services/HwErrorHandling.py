from PyQt5 import QtCore

from services.LoggingService import LoggingService

class HwErrorHandling(QtCore.QObject):
    hwError = QtCore.pyqtSignal(str, str)

    def __init__(self):
        super().__init__()

    def hwErrorEmit(self, info):
        LoggingService.getLogger().error("HW ERROR")
        LoggingService.getLogger().error(info)
        LoggingService.getLogger().error("HW ERROR - END")
        self.hwError.emit(" HW ERROR!!!", info)

