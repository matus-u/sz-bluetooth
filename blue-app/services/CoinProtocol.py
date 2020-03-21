from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

from services import TimerService
from services.LoggingService import LoggingService
import os
import time
import sys, serial

class CoinProtocolStatusObject(TimerService.TimerStatusObject):

    actualStatus = QtCore.pyqtSignal(str)
    coinMachineLockStatus = QtCore.pyqtSignal(bool)

    def __init__(self):
        super().__init__(200)

    def coinMachineLockSlot(self, toLock):
        s = serial.Serial('/dev/ttyS3', baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=None, xonxoff=0, rtscts=0)
        LoggingService.getLogger().info("Coin machine lock request: %s" % str(toLock))
        if toLock:
            s.write(b"@ff00I=0SS\r\n")
        else:
            s.write(b"@ff00I=1SS\r\n")
        s.close()
        self.coinMachineLockStatus.emit(toLock)

    def onTimeout(self):
        s = serial.Serial('/dev/ttyS3', baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=None, xonxoff=0, rtscts=0)
        s.write(b"U@ff00S?bfSS\r\n")
        serialString = str(s.readline().rstrip())[8:26]
        toEmitData = str(serialString)
        if not serialString.startswith("S=0,0,0,0,0,0,00"):
            toSend = list(serialString)
            LoggingService.getLogger().info("SerialString %s" % serialString)
            toSend[0] = 'D'
            serialString = "".join(toSend)
            serialString = serialString[:-2]
            toSend = "U@ff00" + serialString + "SS\r\n"
            s.write(toSend.encode())
        s.close()
        self.actualStatus.emit(toEmitData)
