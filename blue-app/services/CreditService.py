from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

import os
from services.CoinProtocolService import CoinProtocolService
from services.MoneyTracker import MoneyTracker

class CreditBluetoothRepresentation:
    def getCreditValueRepresentation(self, credit, coinSettings):
        return int(credit/coinSettings[7])

class CreditSongRepresentation:
    def getCreditValueRepresentation(self, credit, coinSettings):
        return int(credit/coinSettings[8])

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
        self.credit = self.credit + value
        self.creditChanged.emit(value)

    def setCoinSettings(self, coinSettings):
        self.coinSettings = coinSettings

    def clearCredit(self):
        self.changeCredit(-1 * self.credit)

    def getCredit(self):
        return self.credit

    def getBluetoothRepresentation(self):
        return CreditBluetoothRepresentation().getCreditValueRepresentation(self.credit, self.coinSettings)

    def getSongsRepresentation(self):
        return CreditSongRepresentation().getCreditValueRepresentation(self.credit, self.coinSettings)

    def cleanup(self):
        pass
