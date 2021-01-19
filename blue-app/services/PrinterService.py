import sys, serial
from datetime import datetime
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

from services.AppSettings import AppSettings
from services.LoggingService import LoggingService
from services.HwErrorHandling import HwErrorHandling

import random
import string

from services import PathSettings

def randomString(stringLength):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(stringLength))

class PrintingService(QtCore.QObject):

    printError = QtCore.pyqtSignal()
    lowPaper = QtCore.pyqtSignal()
    lowPaperClear = QtCore.pyqtSignal()
    noPaper = QtCore.pyqtSignal()
    enoughPaper = QtCore.pyqtSignal()
    printStatusUpdated = QtCore.pyqtSignal()
    ticketCounterChanged = QtCore.pyqtSignal()

    SettingsPath = PathSettings.AppBasePath() + "../blue-app-configs/print-tracking.conf"
    SettingsFormat = QtCore.QSettings.NativeFormat

    TicketCounter = "TicketCounter"


    def __init__(self, hwErrorHandler, wheelFortuneService):
        super().__init__()

        self.errorStatus = 0
        self.paperError = 0
        self.statusValid = True

        self.hwErrorHandler = hwErrorHandler

        self.settings = QtCore.QSettings(PrintingService.SettingsPath, PrintingService.SettingsFormat)
        self.ticketCounter = self.settings.value(PrintingService.TicketCounter, 0, int)

        self.noPaper.connect(lambda: hwErrorHandler.hwErrorEmit(HwErrorHandling.NO_PAPER))
        self.enoughPaper.connect(lambda: hwErrorHandler.hwErrorClear(HwErrorHandling.NO_PAPER))
        self.clearPrintCorruptedFunc = lambda: hwErrorHandler.hwErrorClear(HwErrorHandling.PRINTER_CORRUPTED)

        self.testTimer = QtCore.QTimer(self)
        self.testTimer.timeout.connect(self.checkState)

        wheelFortuneService.enabledNotification.connect(lambda enabled: self.onWheelFortuneEnabledNotification(enabled, hwErrorHandler))

        self.initFunc = lambda: self.onWheelFortuneEnabledNotification(wheelFortuneService.isEnabled(), hwErrorHandler)

    def initialize(self):
        self.initFunc()

    def errorFunc(self):
        self.printStatusUpdated.emit()
        self.hwErrorHandler.hwErrorEmit(HwErrorHandling.PRINTER_CORRUPTED)

    def onWheelFortuneEnabledNotification(self, enabled, hwErrorHandler):
        if enabled:
            if not self.testTimer.isActive():
                self.checkState()
                self.testTimer.start(30000)
        else:
            if self.testTimer.isActive():
                self.testTimer.stop()
                self.enoughPaper.emit()
                self.clearPrintCorruptedFunc()

    def readOneByte(self, serial):
        byt = serial.read(1)
        if len(byt) == 0:
            try:
                serial.close()
            except:
                pass
            raise "Read timeout exception"
        return byt

    def checkError(self, s):
        s.write([0x10, 0x04, 0x03])
        self.errorStatus = ord(self.readOneByte(s))

        if self.errorStatus != 18:
            self.printError.emit()

        s.write([0x10, 0x04, 0x04])
        self.paperError = ord(self.readOneByte(s))

        if (self.paperError & 0x8) > 0:
            self.lowPaper.emit()
        else:
            self.lowPaperClear.emit()

        if (self.paperError & 0x40) > 0:
            self.noPaper.emit()
        else:
            self.enoughPaper.emit()

    def getPrintStatus(self):

        if not self.statusValid:
            return { "ticketCounter" : self.ticketCounter,  "errorStatus" : "N/A", "errorStatusValue" : -1, "paperStatus" : "N/A", "paperStatusValue" : -1 }

        errorString = "OK"
        if self.errorStatus != 18:
            errorString = "ERROR"

        paperStatus = "OK"

        if (self.paperError & 0x8) > 0:
            paperStatus = "LOW_PAPER"

        if (self.paperError & 0x40) > 0:
            paperStatus = "NO_PAPER"

        return { "ticketCounter" : self.ticketCounter,  "errorStatus" : errorString, "errorStatusValue" : self.errorStatus, "paperStatus" : paperStatus, "paperStatusValue" : self.paperError }

    def getTicketCounter(self):
        return self.ticketCounter

    def setNewTicketCounter(self, value):
        if value != self.ticketCounter:
            self.ticketCounter = value
            self.settings.setValue(PrintingService.TicketCounter, self.ticketCounter)
            self.ticketCounterChanged.emit()

    def printDescTicket(self, name, prizeCounts, prizeNames, initPrizeCounts):
        try:
            self.statusValid = False
            s = serial.Serial('/dev/ttyS2', baudrate=19200, bytesize=8, parity='N', stopbits=1, timeout=3, xonxoff=0, rtscts=0)
            s.write([0x1b, 0x40])
            s.write(datetime.now().strftime("%H:%M:%S         %d/%m/%Y\n").encode())
            s.write(("DEVICE: " + name + "\n").encode())

            for i in range(1,10):
                s.write((str(i) + " - " + prizeNames[i][0:18] + " - " + str(initPrizeCounts[i]) + "/" + str(prizeCounts[i]) + "\n").encode())

            s.write(b"\n")
            s.write(b"\n")
            s.write(b"\n")
            s.write(b"\n")

            #CUT PAPER#
            s.write([0x1d, 0x56, 0])
            #s.write(b"\n")
            self.checkError(s)
            s.close()

            self.statusValid = True
            self.printStatusUpdated.emit()
            self.clearPrintCorruptedFunc()
        except:
            LoggingService.getLogger().error("PrintingService: printDescTicket: Error func called")
            self.errorFunc()

    def printWithdrawTicket(self, gain, prizes, inkeeperPerc):
        print ("Print withdraw ticket!")
        print ("Gain: %0.2f" % gain)
        print ("InkeeperPerc: %0.2f" % inkeeperPerc)
        print (prizes)

    def printTestTicket(self):
        try:
            self.statusValid = False
            s = serial.Serial('/dev/ttyS2', baudrate=19200, bytesize=8, parity='N', stopbits=1, timeout=3, xonxoff=0, rtscts=0)
            s.write([0x1b, 0x40])
            s.write(datetime.now().strftime("%H:%M:%S         %d/%m/%Y\n").encode())
            s.write(("THIS IS TEST TICKET\n").encode())

            for i in range(1,10):
                s.write(("TEST " + " - " + str(i) + " - "  + "\n").encode())

            s.write(b"\n")
            s.write(b"\n")

            #CUT PAPER#
            s.write([0x1d, 0x56, 0])
            #s.write(b"\n")
            self.checkError(s)
            s.close()

            self.statusValid = True
            self.printStatusUpdated.emit()
            self.clearPrintCorruptedFunc()
        except:
            LoggingService.getLogger().error("PrintingService: printTestTicket: Error func called")
            self.errorFunc()

    def checkState(self):
        try:
            self.statusValid = False
            s = serial.Serial('/dev/ttyS2', baudrate=19200, bytesize=8, parity='N', stopbits=1, timeout=3, xonxoff=0, rtscts=0)
            self.checkError(s)
            s.close()
            self.statusValid = True
            self.printStatusUpdated.emit()
            self.clearPrintCorruptedFunc()
        except:
            LoggingService.getLogger().error("Check state func called")
            self.errorFunc()

    def printTicket(self, name, winNumber, prizeName):
        try:
            self.statusValid = False
            s = serial.Serial('/dev/ttyS2', baudrate=19200, bytesize=8, parity='N', stopbits=1, timeout=3, xonxoff=0, rtscts=0)

            s.write([0x1b, 0x40])
            s.write(datetime.now().strftime("%H:%M:%S         %d/%m/%Y\n").encode())
            s.write([0x1b, 0x4D, 49])
            s.write([0x1b, 0x4A, 10])
            s.write([0x1d, 0x21, 0x11])
            s.write(b"\n")
            s.write(b"      MUSICBOX\n")
            s.write(("         #"+ str(winNumber) +"\n").encode())
            s.write((" "+ prizeName[0:20] + "\n").encode())
            s.write(b"\n")
            s.write([0x1d, 0x21, 0x00])
            s.write([0x1d, 0x21, 0x71])
            s.write((self.tr("DEVICE: ") + name + "\n").encode(encoding='cp437'))
            s.write(("ID: "+ randomString(8) +"\n").encode(encoding='cp437'))
            s.write(self.tr("Thank you for playing!\n").encode(encoding='cp437'))
            s.write(b"\n")
            s.write(b"\n")
            s.write(b"\n")

            #CUT PAPER#
            s.write([0x1d, 0x56, 0])
            #s.write(b"\n")
            self.checkError(s)
            s.close()

            self.statusValid = True
            self.ticketCounter = self.ticketCounter + 1
            self.printStatusUpdated.emit()
            self.clearPrintCorruptedFunc()
            self.settings.setValue(PrintingService.TicketCounter, self.ticketCounter)
        except:
            LoggingService.getLogger().error("PrintingService: printTicket: Error func called")
            self.errorFunc()

