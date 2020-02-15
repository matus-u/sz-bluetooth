import sys, serial
from datetime import datetime
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

class PrintingService(QtCore.QObject):

    printError = QtCore.pyqtSignal()
    lowPaper = QtCore.pyqtSignal()
    noPaper = QtCore.pyqtSignal()
    printFinished = QtCore.pyqtSignal()

    def __init__(self, hwErrorHandler):
        super().__init__()

        self.errorStatus = 0
        self.paperError = 0
        self.errorFunc = lambda: hwErrorHandler.hwErrorEmit("Printer machine corrupted! Call service!")

    def initialize(self):
        try:
            s = serial.Serial('/dev/ttyS2', baudrate=19200, bytesize=8, parity='N', stopbits=1, timeout=None, xonxoff=0, rtscts=0)
            s.write([0x1b, 0x40])
            s.write(b"\n")
            s.write(b"\n")
            s.write(b"\n")
            s.write(b"\n")
            s.write([0x1d, 0x56, 0])
            self.checkError(s)
            s.close()

            self.printFinished.emit()
        except:
            self.errorFunc()

    def printTicket(self, name, ID, winNumber):
        try:
            s = serial.Serial('/dev/ttyS2', baudrate=19200, bytesize=8, parity='N', stopbits=1, timeout=None, xonxoff=0, rtscts=0)

            s.write([0x1b, 0x40])
            s.write(datetime.now().strftime("%H:%M:%S         %d/%m/%Y\n").encode())
            s.write([0x1b, 0x4D, 49])
            s.write([0x1b, 0x4A, 10])
            s.write([0x1d, 0x21, 0x11])
            s.write(b"\n")
            s.write(b"      MUSICBOX\n")
            s.write(("         #"+ str(winNumber) +"\n").encode())
            s.write(b"\n")
            s.write([0x1d, 0x21, 0x00])
            s.write([0x1d, 0x21, 0x71])

            s.write(("DEVICE: " + name + "\n").encode())
            #s.write(b"ID:\n")
            s.write(b"\n")
            s.write(b"\n")
            s.write(b"\n")

            #CUT PAPER#
            s.write([0x1d, 0x56, 0])
            #s.write(b"\n")
            self.checkError(s)
            s.close()

            self.printFinished.emit()
        except:
            self.errorFunc()

    def checkError(self, s):
        s.write([0x10, 0x04, 0x03])
        ret = ord(s.read(1))
        self.errorStatus = ret

        if ret != 18:
            self.printError.emit()

        s.write([0x10, 0x04, 0x04])
        ret = ord(s.read(1))
        self.paperError = ret

        if (ret & 0x8) > 0:
            self.lowPaper.emit()

        if (ret & 0x40) > 0:
            self.noPaper.emit()

    def getErrorDesc(self):
        errorString = "OK"
        if self.errorStatus != 18:
            errorString = "ERROR"

        paperStatus = "OK"

        if (self.paperError & 0x8) > 0:
            paperStatus = "LOW_PAPER"

        if (self.paperError & 0x40) > 0:
            paperStatus = "NO_PAPER"

        return { "errorStatus" : errorString, "errorStatusValue" : self.errorStatus, "paperStatus" : paperStatus, "paperStatusValue" : self.paperError }

    def getErrorStatus(self):
        return self.errorStatus

    def printDescTicket(self, name, prizeCounts, prizeNames):
        try:
            s = serial.Serial('/dev/ttyS2', baudrate=19200, bytesize=8, parity='N', stopbits=1, timeout=None, xonxoff=0, rtscts=0)
            s.write([0x1b, 0x40])
            s.write(datetime.now().strftime("%H:%M:%S         %d/%m/%Y\n").encode())
            s.write(("DEVICE: " + name + "\n").encode())

            for i in range(1,10):
                s.write((str(i) + " - " + prizeNames[i] + " - " + str(prizeCounts[i]) + "\n").encode())

            s.write(b"\n")
            s.write(b"\n")

            #CUT PAPER#
            s.write([0x1d, 0x56, 0])
            #s.write(b"\n")
            self.checkError(s)
            s.close()

            self.printFinished.emit()
        except:
            self.errorFunc()
