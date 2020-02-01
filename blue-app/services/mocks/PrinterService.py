from datetime import datetime
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

class PrintingService(QtCore.QObject):

    def __init__(self):
        super().__init__()

    def printTicket(self, name, ID, winNumber):
        print ("NAME {} ID {} winNumber {}".format(name,ID,winNumber))

