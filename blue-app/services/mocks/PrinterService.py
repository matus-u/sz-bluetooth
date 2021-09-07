from datetime import datetime
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

from services.HwErrorHandling import HwErrorHandling
from services import PathSettings

class PrintingService(QtCore.QObject):

    printError = QtCore.pyqtSignal()
    lowPaper = QtCore.pyqtSignal()
    lowPaperClear = QtCore.pyqtSignal()
    noPaper = QtCore.pyqtSignal()
    enoughPaper = QtCore.pyqtSignal()
    printStatusUpdated = QtCore.pyqtSignal()
    ticketCounterChanged = QtCore.pyqtSignal()

    SettingsPath = PathSettings.AppBasePath() + "../blue-app-configs/print-tracking.conf"

    def __init__(self, hwErrorHandler):
        super().__init__()
        self.errorFunc = lambda: hwErrorHandler.hwErrorEmit(HwErrorHandling.PRINTER_CORRUPTED)
        self.ticketCounter = 0

        QtCore.QTimer.singleShot(10000, lambda: hwErrorHandler.hwErrorEmit(HwErrorHandling.PRINTER_CORRUPTED))
        QtCore.QTimer.singleShot(11000, lambda: hwErrorHandler.hwErrorEmit(HwErrorHandling.NO_PAPER))

    def initialize(self):
        self.printStatusUpdated.emit()
        #self.errorFunc()

    def printTicket(self, name, winNumber, prizeName):
        print ("NAME {} winNumber {} prize name: {}".format(name,winNumber, prizeName))
        self.printStatusUpdated.emit()

    def getPrintStatus(self):
        return { "ticketCounter" : self.ticketCounter, "errorStatus" : "OK", "errorStatusValue" : 25, "paperStatus" : "LOW_PAPER", "paperStatusValue" : 15 }

    def printDescTicket(self, name, prizeCounts, prizeNames, initPrizeCounts):
        print (name)
        print (prizeCounts)
        print (prizeNames)
        print (initPrizeCounts)

    def setNewTicketCounter(self, value):
        if value != self.ticketCounter:
            self.ticketCounter = value
            self.ticketCounterChanged.emit()

    def getTicketCounter(self):
        return self.ticketCounter

    def printTestTicket(self):
        print ("Print test ticket!")

    def printWithdrawTicket(self, device, gain, prizes, inkeeperPerc, currency, owner, swVersion, moneyTotal, moneyFromLastWithdraw):
        print("DEVICE: " + device)
        print("OWNER: " + owner)
        print(datetime.now().strftime("%H:%M:%S         %d/%m/%Y"))
        print("CURRENCY: " + currency)
        print("SW-version: " + swVersion)
        print("Ticket counter: " + str(self.ticketCounter))
        print("Money total: " + "{0:g}".format(moneyTotal))
        print("Money from withdraw: " + "{0:g}".format(moneyFromLastWithdraw))
        print("Total gain: " + "{0:g}".format(gain))
        inkeeperGain = gain * inkeeperPerc /100 if gain > 0 else 0
        ownerGain = gain - inkeeperGain if gain > 0 else 0
        print("Gain owner: " + "{0:g}".format(ownerGain))
        print("Gain inkeeper: " + "{0:g}".format(inkeeperGain))
        print("Won prizes: ")

        for key, count in prizes.items():
            name, prize = key.rsplit('-',1)
            print(str(name) + " - " + str(prize) + " - " + str(count))

