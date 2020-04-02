from datetime import datetime
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

from services.HwErrorHandling import HwErrorHandling

class PrintingService(QtCore.QObject):

    printError = QtCore.pyqtSignal()
    lowPaper = QtCore.pyqtSignal()
    noPaper = QtCore.pyqtSignal()
    printFinished = QtCore.pyqtSignal()
    ticketCounterChanged = QtCore.pyqtSignal()

    def __init__(self, hwErrorHandler, wheelFortuneService):
        super().__init__()
        self.errorFunc = lambda: hwErrorHandler.hwErrorEmit("Printer machine corrupted! Call service!")
        self.ticketCounter = 0

        #QtCore.QTimer.singleShot(10000, lambda: hwErrorHandler.hwErrorEmit(HwErrorHandling.COIN_MACHINE_CORRUPTED))

    def initialize(self):
        self.printFinished.emit()
        #self.errorFunc()

    def printTicket(self, name, winNumber, prizeName):
        print ("NAME {} winNumber {} prize name: {}".format(name,winNumber, prizeName))
        self.printFinished.emit()

    def getPrintStatus(self):
        return { "ticketCounter" : self.ticketCounter, "errorStatus" : "OK", "errorStatusValue" : 25, "paperStatus" : "LOW_PAPER", "paperStatusValue" : 15 }

    def printDescTicket(self, name, prizeCounts, prizeNames):
        print (name)
        print (prizeCounts)
        print (prizeNames)

    def setNewTicketCounter(self, value):
        if value != self.ticketCounter:
            self.ticketCounter = value
            self.ticketCounterChanged.emit()

    def getTicketCounter(self):
        return self.ticketCounter

    def printTestTicket(self):
        print ("Print test ticket!")
