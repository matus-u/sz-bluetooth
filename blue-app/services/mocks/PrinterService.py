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
        self.errorFunc = lambda: hwErrorHandler.hwErrorEmit("Printer machine corrupted! Call service!")

    def initialize(self):
        self.printFinished.emit()
        #self.errorFunc()

    def printTicket(self, name, ID, winNumber):
        print ("NAME {} ID {} winNumber {}".format(name,ID,winNumber))
        self.printFinished.emit()

    def getErrorDesc(self):
        return { "errorStatus" : "OK", "errorStatusValue" : 25, "paperStatus" : "LOW_PAPER", "paperStatusValue" : 15 }

    def printDescTicket(self, name, prizeCounts, prizeNames):
        print (name)
        print (prizeCounts)
        print (prizeNames)
