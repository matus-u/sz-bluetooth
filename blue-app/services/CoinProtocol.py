from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

from services import TimerService
from services.LoggingService import LoggingService
from services.HwErrorHandling import HwErrorHandling
import os
import time
import sys, serial
import struct

class CoinProtocolStatusObject(TimerService.TimerStatusObject):

    actualStatus = QtCore.pyqtSignal(str)
    coinMachineLockStatus = QtCore.pyqtSignal(bool)
    serialError = QtCore.pyqtSignal()

    def __init__(self, hwErrorHandler):
        super().__init__(200)

        self.serialError.connect(lambda: hwErrorHandler.hwErrorEmit(HwErrorHandling.COIN_MACHINE_CORRUPTED), QtCore.Qt.QueuedConnection)

    def coinMachineLockSlot(self, toLock):
        try:
            s = serial.Serial('/dev/ttyS3', baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=5, xonxoff=0, rtscts=0)
            LoggingService.getLogger().info("Coin machine lock request: %s" % str(toLock))
            if toLock:
                s.write(b"@ff00I=0SS\r\n")
            else:
                s.write(b"@ff00I=1SS\r\n")
            s.close()
            self.coinMachineLockStatus.emit(toLock)
        except:
            LoggingService.getLogger().info("CoinProtocolStatusObject: coinMachineLockStatus: Lock status hw error!")
            self.serialError.emit()

    def onTimeout(self):
        try:
            s = serial.Serial('/dev/ttyS3', baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=5, xonxoff=0, rtscts=0)
            s.write(b"U@ff00S?bfSS\r\n")
            byteArray = s.readline()
            if len(byteArray) == 0:
                serial.close()
                raise "Serial read timeout exception"
            serialString = str(byteArray.rstrip())[8:26]
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
        except:
            LoggingService.getLogger().info("CoinProtocolStatusObject: onTimeout: CPU communication error!")
            self.serialError.emit()

    def storePersistentCredit(self, value):
        creditBytes = bytearray(struct.pack('d', value))

        s = serial.Serial('/dev/ttyS3', baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=5, xonxoff=0, rtscts=0)
        s.write(b"U@ff00K?SS\r\n")
        serialString = s.read(54)[8:-6]
        byteArray = bytearray.fromhex(serialString.decode())
        for i in range(0,8):
            byteArray[i] = creditBytes[i]

        su = 0
        for x in byteArray:
            su = su+x
            su = su % 256
        byteArray.append(su)

        toWrite = "U@ff00K="+byteArray.hex()+"SS\r\n"
        s.write(toWrite.encode())
        print (s.readline())
        s.close()


    def readPersistentValue(self):
        creditBytes = []

        s = serial.Serial('/dev/ttyS3', baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=5, xonxoff=0, rtscts=0)
        s.write(b"U@ff00K?SS\r\n")

        serialString = s.read(54)[8:-6]
        s.close()

        byteArray = bytearray.fromhex(serialString.decode("utf-8"))
        for i in range(0,8):
            creditBytes.append(byteArray[i])
        return struct.unpack('d', bytes(creditBytes))[0]


