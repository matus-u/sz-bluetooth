from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

from services import TimerService
from services.LoggingService import LoggingService
import os
import time


class CoinProtocolStatusObject(TimerService.TimerStatusObject):

    actualStatus = QtCore.pyqtSignal(str)
    coinMachineLockStatus = QtCore.pyqtSignal(bool)

    def __init__(self, hwStatusHandler):
        super().__init__(200)

    def coinMachineLockSlot(self, toLock):
        LoggingService.getLogger().info("Coin machine lock request: %s" % str(toLock))
        self.coinMachineLockStatus.emit(toLock)

    def onTimeout(self):
        self.actualStatus.emit("S=0,0,0,0,0,0,0021")


    def storePersistentCredit(self, value):
        print ("STORING " + str(value))

    def readPersistentValue(self):
        print ("READING")
        return 10
