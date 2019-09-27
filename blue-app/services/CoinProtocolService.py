from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

from services import TimerService
from services.LoggingService import LoggingService
import os
import time

class CoinProtocolStatusObject(TimerService.TimerStatusObject):

    actualStatus = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__(200)

    def onTimeout(self):
        if os.getenv('RUN_FROM_DOCKER', False) == False:
            import sys, serial
            s = serial.Serial('/dev/ttyS3', baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=None, xonxoff=0, rtscts=0)
            s.write(b"U@ff00S?bfSS\r\n")
            serialString = str(s.readline().rstrip())[8:26]
            self.actualStatus.emit(str(serialString))
            if not serialString.startswith("S=0,0,0,0,0,0,00"):
                toSend = list(serialString)
                LoggingService.getLogger().info("SerialString %s" % serialString)
                toSend[0] = 'D'
                serialString = "".join(toSend)
                serialString = serialString[:-2]
                toSend = "U@ff00" + serialString + "SS\r\n"
                s.write(toSend.encode())
        else:
            self.actualStatus.emit("S=0,0,0,0,0,0,0021")

class CoinProtocolService(QtCore.QObject):
    actualStatus = QtCore.pyqtSignal(int, int)
    def __init__(self):
        super().__init__()
        self.thread = QtCore.QThread()
        self.thread.start()
        self.statusObject = CoinProtocolStatusObject()
        self.statusObject.actualStatus.connect(lambda x: self.onCoinStatus(x), QtCore.Qt.QueuedConnection)
        TimerService.addTimerWorker(self.statusObject, self.thread)
        self.statusObject.start()

    def onCoinStatus(self, stringValues):
        for idx, val in enumerate(stringValues[2:-2].split(",")):
            self.actualStatus.emit(int(idx),int(val))
