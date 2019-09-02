from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

import os
from services.CoinProtocolService import CoinProtocolService


class CreditService(QtCore.QObject):
    creditChanged = QtCore.pyqtSignal(float)

    def __init__(self, coinSettings):
        super().__init__()
        self.credit = 0.0
        self.coinSettings = coinSettings
        self.coinService = CoinProtocolService()
        self.coinService.actualStatus.connect(self.onCoinChannel)
                

    def onCoinChannel(self, channel, count):
        self.changeCredit((self.coinSettings[channel] * count) / self.coinSettings[7])

    def changeCredit(self, value):
        self.credit = self.credit + value
        self.creditChanged.emit(value)

    def setCoinSettings(self, coinSettings):
        self.coinSettings = coinSettings

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
