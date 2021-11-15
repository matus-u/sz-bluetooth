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
    clearPrint = QtCore.pyqtSignal()
    errorEmit = QtCore.pyqtSignal()

    runFunc = QtCore.pyqtSignal(object)

    SettingsPath = PathSettings.AppBasePath() + "../blue-app-configs/print-tracking.conf"
    SettingsFormat = QtCore.QSettings.NativeFormat

    TicketCounter = "TicketCounter"


    def __init__(self, hwErrorHandler):
        super().__init__()

        self.errorStatus = 0
        self.paperError = 0
        self.statusValid = True

        self.hwErrorHandler = hwErrorHandler


        self.testTimer = QtCore.QTimer()

        self.thread = QtCore.QThread()
        self.moveToThread(self.thread)
        self.testTimer.moveToThread(self.thread)
        self.thread.start()

        self.settings = QtCore.QSettings(PrintingService.SettingsPath, PrintingService.SettingsFormat)
        self.ticketCounter = self.settings.value(PrintingService.TicketCounter, 0, int)

        self.noPaper.connect(lambda: hwErrorHandler.hwErrorEmit(HwErrorHandling.NO_PAPER), QtCore.Qt.QueuedConnection)
        self.enoughPaper.connect(lambda: hwErrorHandler.hwErrorClear(HwErrorHandling.NO_PAPER), QtCore.Qt.QueuedConnection)
        self.clearPrint.connect(lambda: hwErrorHandler.hwErrorClear(HwErrorHandling.PRINTER_CORRUPTED), QtCore.Qt.QueuedConnection)
        self.errorEmit.connect(lambda: hwErrorHandler.hwErrorEmit(HwErrorHandling.PRINTER_CORRUPTED), QtCore.Qt.QueuedConnection)
        self.runFunc.connect(self.onRunFunc, QtCore.Qt.QueuedConnection)

        self.testTimer.timeout.connect(self.checkState)

    def initialize(self):
        def _initialize():
            self.onWheelFortuneEnabledNotification(True, self.hwErrorHandler)
        self.runFunc.emit(_initialize)

    def errorFunc(self):
        self.printStatusUpdated.emit()
        self.errorEmit.emit()

    def onWheelFortuneEnabledNotification(self, enabled, hwErrorHandler):
        if enabled:
            if not self.testTimer.isActive():
                self.checkState()
                self.testTimer.start(30000)
        else:
            if self.testTimer.isActive():
                self.testTimer.stop()
                self.enoughPaper.emit()
                self.clearPrint.emit()

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
            LoggingService.getLogger().error("PrintingService: error: {}".format(self.errorStatus))

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
        def _setNewTicketCounter():
            if value != self.ticketCounter:
                self.ticketCounter = value
                self.settings.setValue(PrintingService.TicketCounter, self.ticketCounter)
                self.ticketCounterChanged.emit()
        self.runFunc.emit(_setNewTicketCounter)

    def printDescTicket(self, name, prizeCounts, prizeNames, initPrizeCounts):
        def _printDescTicket():
            try:
                self.statusValid = False
                s = serial.Serial('/dev/ttyS2', baudrate=19200, bytesize=8, parity='N', stopbits=1, timeout=3, xonxoff=0, rtscts=0)
                s.write([0x1b, 0x40])
                s.write(datetime.now().strftime("%H:%M:%S         %d/%m/%Y\n").encode())
                s.write(("DEVICE: " + name + "\n").encode(encoding='cp852'))

                for i in range(1,10):
                    s.write((str(i) + " - " + prizeNames[i][0:18] + " - " + str(initPrizeCounts[i]) + "/" + str(prizeCounts[i]) + "\n").encode(encoding='cp852'))

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
                self.clearPrint.emit()
            except Exception as e:
                LoggingService.getLogger().error("PrintingService: printDescTicket: Error func called {}".format(e))
                self.errorFunc()
        self.runFunc.emit(_printDescTicket)

    def printWithdrawTicket(self, device, gain, prizes, inkeeperPerc, currency, owner, swVersion, moneyTotal, moneyFromLastWithdraw):
        def printWithInt():
            try:
                self.ticketCounter = self.ticketCounter + 1
                self.statusValid = False
                s = serial.Serial('/dev/ttyS2', baudrate=19200, bytesize=8, parity='N', stopbits=1, timeout=3, xonxoff=0, rtscts=0)
                s.write([0x1b, 0x40])
                s.write(("DEVICE: " + device + "\n").encode(encoding='cp852'))
                s.write(("OWNER: " + owner + "\n").encode(encoding='cp852'))
                s.write(datetime.now().strftime("%H:%M:%S         %d/%m/%Y\n").encode())
                s.write(("CURRENCY: " + currency + "\n").encode())
                s.write(("SW-version: " + swVersion + "\n").encode())
                s.write(("Ticket counter: " + str(self.ticketCounter) + "\n").encode())
                s.write(("Money total: " + "{0:g}".format(moneyTotal) + "\n").encode())
                s.write(("Money from withdraw: " + "{0:g}".format(moneyFromLastWithdraw) + "\n").encode())
                s.write(("Total gain: " + "{0:g}".format(gain) + "\n").encode())
                inkeeperGain = gain * inkeeperPerc /100 if gain > 0 else 0
                ownerGain = gain - inkeeperGain if gain > 0 else 0
                s.write(("Gain owner: " + "{0:g}".format(ownerGain) + "\n").encode())
                s.write(("Gain inkeeper: " + "{0:g}".format(inkeeperGain) + "\n").encode())
                s.write(("Won prizes: " + "\n").encode())

                for key, count in prizes.items():
                    name, prize = key.rsplit('-',1)
                    s.write((name[0:18] + "/" + "{0:g}".format(float(prize)) + "/" + str(count) + "x\n").encode(encoding='cp852'))

                s.write(b"\n")
                s.write(b"\n")
                s.write(b"\n")
                s.write(b"\n")

                #CUT PAPER#
                s.write([0x1d, 0x56, 0])
                #s.write(b"\n")
                self.checkError(s)
                s.close()
                LoggingService.getLogger().info("Printed  withdraw ticket!")

                self.statusValid = True
                self.printStatusUpdated.emit()
                self.clearPrint.emit()
                self.settings.setValue(PrintingService.TicketCounter, self.ticketCounter)
            except Exception as e:
                LoggingService.getLogger().error("PrintingService: printWithdrawTicket: Error func called {}".format(e))
                self.errorFunc()

        self.runFunc.emit(printWithInt)
        self.runFunc.emit(printWithInt)

    def printTestTicket(self):
        def _printTestTicket():
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
                self.clearPrint.emit()
            except Exception as e:
                LoggingService.getLogger().error("PrintingService: printTestTicket: Error func called {}".format(e))
                self.errorFunc()
        self.runFunc.emit(_printTestTicket)

    def checkState(self):
        try:
            self.statusValid = False
            s = serial.Serial('/dev/ttyS2', baudrate=19200, bytesize=8, parity='N', stopbits=1, timeout=3, xonxoff=0, rtscts=0)
            self.checkError(s)
            s.close()
            self.statusValid = True
            self.printStatusUpdated.emit()
            self.clearPrint.emit()
        except Exception as e:
            LoggingService.getLogger().error("Check state func called {}".format(e))
            self.errorFunc()

    def printTicket(self, name, winNumber, prizeName):
        def _printTicket():
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
                s.write((" "+ prizeName[0:20] + "\n").encode(encoding='cp852'))
                s.write(b"\n")
                s.write([0x1d, 0x21, 0x00])
                s.write([0x1d, 0x21, 0x71])
                s.write((self.tr("DEVICE: ") + name + "\n").encode(encoding='cp852'))
                s.write(("ID: "+ randomString(8) +"\n").encode(encoding='cp852'))
                s.write(self.tr("Thank you for playing!\n").encode(encoding='cp852'))
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
                self.clearPrint.emit()
                self.settings.setValue(PrintingService.TicketCounter, self.ticketCounter)
            except Exception as e:
                LoggingService.getLogger().error("PrintingService: printTicket: Error func called {}".format(e))
                self.errorFunc()
        self.runFunc.emit(_printTicket)

    def onRunFunc(self, func):
        func()
