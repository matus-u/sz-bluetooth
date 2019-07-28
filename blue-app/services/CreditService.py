from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

import os

class CreditService(QtCore.QObject):
    creditChanged = QtCore.pyqtSignal(float)

    def __init__(self, currency):
        print (os.getenv('RUN_FROM_DOCKER', False))
        super().__init__()
        self.credit = 0.0
        self.actualCurrency = currency

        # TODO LOAD FROM FILE
        self.currencyMap = { 29 : ["EUR", 0.50],
                             31 : ["EUR", 1.0],
                             33 : ["HUF", 50],
                             35 : ["HUF", 100],
                             37 : ["HUF", 200]}
        if os.getenv('RUN_FROM_DOCKER', False) == False:
            from services.GpioService import GpioService
            self.gpio = GpioService()
            for pin, data in self.currencyMap.items():
                self.gpio.registerCallback(pin, self.onGpio)

    def onGpio(self, channel):
        if self.actualCurrency == self.currencyMap[channel][0]:
            self.changeCredit(self.currencyMap[channel][1])

    def changeCredit(self, value):
        self.credit = self.credit + value
        self.creditChanged.emit(self.credit)

    def setCurrency(self, currency):
        self.actualCurrency = currency

    def clearCredit(self):
        self.changeCredit(-1 * self.credit)

    def getCredit(self):
        return self.credit

    def cleanup(self):
        if os.getenv('RUN_FROM_DOCKER', False) == False:
            for pin, data in self.currencyMap.items():
                self.gpio.deregisterCallback(pin)
            self.gpio.cleanup()
