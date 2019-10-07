from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

import os
from services.CoinProtocolService import CoinProtocolService
from services.MoneyTracker import MoneyTracker

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
        self.changeCredit(money / self.coinSettings[7])
        self.moneyInserted.emit(money)

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
