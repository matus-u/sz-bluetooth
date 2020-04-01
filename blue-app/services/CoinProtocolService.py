from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

from services import TimerService
from services.LoggingService import LoggingService
import os
import time

if os.getenv('RUN_FROM_DOCKER', False) == False:
    from services import CoinProtocol
else:
    from services.mocks import CoinProtocol

class CoinProtocolService(QtCore.QObject):
    actualStatus = QtCore.pyqtSignal(int, int)
    coinMachineLockRequest = QtCore.pyqtSignal(bool)

    def __init__(self, hwErrorHandler):
        super().__init__()
        self.locked = False
        self.errorFunc = lambda: hwErrorHandler.hwErrorEmit("Coin machine corrupted! Call service!")
        self.thread = QtCore.QThread()
        self.thread.start()
        self.statusObject = CoinProtocol.CoinProtocolStatusObject(hwErrorHandler)
        self.statusObject.actualStatus.connect(lambda x: self.onCoinStatus(x), QtCore.Qt.QueuedConnection)
        self.statusObject.coinMachineLockStatus.connect(lambda x: self.onCoinMachineLockStatus(x), QtCore.Qt.QueuedConnection)
        self.coinMachineLockRequest.connect(lambda x: self.statusObject.coinMachineLockSlot(x), QtCore.Qt.QueuedConnection)
        TimerService.addTimerWorker(self.statusObject, self.thread)
        self.statusObject.start()

    def lockCoinMachine(self, toLock):
        self.coinMachineLockRequest.emit(toLock)

    def onCoinStatus(self, stringValues):
        for idx, val in enumerate(stringValues[2:-2].split(",")):
            if idx < 6 and self.locked and int(val) > 0:
                self.errorFunc()
                LoggingService.getLogger().error("Coin machine corrupted!")
                return
            self.actualStatus.emit(int(idx),int(val))

    def onCoinMachineLockStatus(self, locked):
        self.locked = locked
