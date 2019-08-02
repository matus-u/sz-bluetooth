from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

import os
from services.CoinProtocolService import CoinProtocolService


class CreditService(QtCore.QObject):
    creditChanged = QtCore.pyqtSignal(float)

    def __init__(self, currency):
        super().__init__()
        self.credit = 0.0
        self.actualCurrency = currency

        # TODO LOAD FROM FILE
        self.currencyMap = { 0 : ["EUR", 0.50],
                             1 : ["EUR", 1.0],
                             2 : ["HUF", 50],
                             3 : ["HUF", 75],
                             4 : ["HUF", 100],
                             5 : ["HUF", 150],
                             6 : ["HUF", 200]}

        self.coinService = CoinProtocolService()
        self.coinService.actualStatus.connect(self.onCoinChannel)
                

    def onCoinChannel(self, channel, count):
        if self.actualCurrency == self.currencyMap[channel][0]:
            self.changeCredit(self.currencyMap[channel][1] * count)

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
        pass

#        if os.getenv('RUN_FROM_DOCKER', False) == False:
#            from services.GpioService import GpioService
#            self.gpio = GpioService()
#            for pin, data in self.currencyMap.items():
#                self.gpio.registerCallback(pin, self.onGpio)

#        if os.getenv('RUN_FROM_DOCKER', False) == False:
#            for pin, data in self.currencyMap.items():
#                self.gpio.deregisterCallback(pin)
#            self.gpio.cleanup()
