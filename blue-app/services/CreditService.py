from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

import os
from services.CoinProtocolService import CoinProtocolService
from services.MoneyTracker import MoneyTracker

class CreditBluetoothRepresentation:
    def __init__(self, creditService):
        self.creditService = creditService

    def getCreditValueRepresentation(self):
        return int(self.creditService.getCredit()/(self.creditService.getCoinSettings()[7]))

    def enoughMoney(self):
        return self.creditService.getCredit() > 0

    def overTakeMoney(self):
        pass

class CreditSongRepresentation:
    def __init__(self, creditService):
        self.creditService = creditService

    def getCreditValueRepresentation(self):
        return int(self.creditService.getCredit()/(self.creditService.getCoinSettings()[8]))

    def enoughMoney(self):
        return self.creditService.getCredit() >= self.creditService.getCoinSettings()[8]

    def overTakeMoney(self):
        return self.creditService.changeCredit(-1*self.creditService.getCoinSettings()[8])

class CreditService(QtCore.QObject):
    creditChanged = QtCore.pyqtSignal(float)
    moneyInserted = QtCore.pyqtSignal(float)

    def __init__(self, coinSettings):
        super().__init__()
        self.credit = 0.0
        self.coinSettings = coinSettings
        self.coinService = CoinProtocolService()
        self.coinService.actualStatus.connect(self.onCoinChannel)

    def onCoinChannel(self, channel, count):
        money = self.coinSettings[channel] * count
        if money != 0:
            self.changeCredit(money)
            self.moneyInserted.emit(money)

    def changeCredit(self, value):
        self.credit = round (self.credit + round(value, 2), 2)
        self.creditChanged.emit(value)

    def setCoinSettings(self, coinSettings):
        self.coinSettings = coinSettings

    def getCoinSettings(self):
        return self.coinSettings

    def clearCredit(self):
        self.changeCredit(-1 * self.credit)

    def getCredit(self):
        return self.credit

    def getBluetoothRepresentation(self):
        return CreditBluetoothRepresentation(self)

    def getSongsRepresentation(self):
        return CreditSongRepresentation(self)

    def cleanup(self):
        pass
