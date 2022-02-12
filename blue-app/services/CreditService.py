from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

import os
from services.CoinProtocolService import CoinProtocolService
from services.MoneyTracker import MoneyTracker
from services.LoggingService import LoggingService
from services.AppSettings import CoinSettingsIndexes, AppSettings

class BonusCounter:
    def __init__(self):
        self.bonusSongs = 0
        self.bonusThreshold = 0
        self.actualBonusAmount = 0
        self.resetNewCurrency()

    def addCredit(self, amount):
        self.actualBonusAmount = self.actualBonusAmount + amount
        while self.actualBonusAmount >= self.bonusThreshold:
            self.bonusSongs = self.bonusSongs + 1
            self.actualBonusAmount = self.actualBonusAmount - self.bonusThreshold

    def resetNewCurrency(self):
        self.bonusSongs = 0
        self.actualBonusAmount = 0
        self.bonusThreshold = AppSettings.currencyClass().bonusThreshold()

    def resetActualBonusAmount(self):
        self.actualBonusAmount = 0

    def resetBonusSongs(self):
        self.bonusSongs = 0

    def lowerBonusSongs(self):
        if self.bonusSongs > 0:
            self.bonusSongs = self.bonusSongs - 1

class CreditBluetoothRepresentation:
    def __init__(self, creditService):
        self.creditService = creditService

    def _calcValueRepr(self, value):
        return int((value/(self.creditService.getCoinSettings()[CoinSettingsIndexes.MINUTE_COST_VALUE]))*60)

    def getCreditValueRepresentation(self):
        return self._calcValueRepr(self.creditService.getCredit())

    def enoughMoney(self):
        return self.creditService.getCredit() > 0

    def overTakeMoney(self):
        LoggingService.getLogger().info("Bluetooth overtake money!")
        credit = self.creditService.getCredit()
        bluetoothThreshold = self.creditService.getCoinSettings()[CoinSettingsIndexes.MONEY_BLUETOOTH_OVERTAKING_VALUE]

        self.creditService.bonusCounter.resetActualBonusAmount()
        self.creditService.bonusCounter.resetBonusSongs()

        if credit > bluetoothThreshold:
            self.creditService.changeCredit(-1*bluetoothThreshold)
            return self._calcValueRepr(bluetoothThreshold)

        self.creditService.clearCredit()
        return self._calcValueRepr(credit)

class CreditSongRepresentation:
    def __init__(self, creditService):
        self.creditService = creditService

    def getCreditValueRepresentation(self):
        creditValue =  int(self.creditService.getCredit()/(self.creditService.getCoinSettings()[CoinSettingsIndexes.SONG_COST_VALUE]))
        return creditValue + self.creditService.bonusCounter.bonusSongs

    def enoughMoney(self):
        if self.creditService.bonusCounter.bonusSongs > 0:
            return True
        return self.creditService.getCredit() >= self.creditService.getCoinSettings()[CoinSettingsIndexes.SONG_COST_VALUE]

    def overTakeMoney(self):

        self.creditService.bonusCounter.resetActualBonusAmount()

        LoggingService.getLogger().info("Credit song overtake money!")
        if self.creditService.bonusCounter.bonusSongs > 0:
            self.creditService.bonusCounter.lowerBonusSongs()
            self.creditService.creditChanged.emit(0)
            return

        self.creditService.changeCredit(-1*self.creditService.getCoinSettings()[CoinSettingsIndexes.SONG_COST_VALUE])

class CreditService(QtCore.QObject):
    creditChanged = QtCore.pyqtSignal(float)
    moneyInserted = QtCore.pyqtSignal(float)
    creditCleared = QtCore.pyqtSignal()

    def __init__(self, coinSettings, coinLockLevel, errorHandler, testModeService):
        super().__init__()
        self.credit = 0.0
        self.coinSettings = coinSettings
        self.coinLockLevel = coinLockLevel
        self.coinService = CoinProtocolService(errorHandler)
        self.bonusCounter = BonusCounter()

        testModeService.testModeEnabled.connect(self.disConnectActualStatus)
        testModeService.testModeDisabled.connect(self.connectActualStatus)
        self.credit = self.coinService.getStartCreditValue()
        self.connectActualStatus()

    def connectActualStatus(self):
        self.coinService.actualStatus.connect(self.onCoinChannel)

    def disConnectActualStatus(self):
        self.coinService.actualStatus.disconnect(self.onCoinChannel)

    def onCoinChannel(self, channel, count):
        money = self.coinSettings[channel] * count
        if money != 0:
            self.bonusCounter.addCredit(money)
            self.changeCredit(money)
            self.moneyInserted.emit(money)
            LoggingService.getLogger().info("Money inserted " + str(money))

    def changeCredit(self, value):
        self.credit = round (self.credit + round(value, 2), 2)
        self.creditChanged.emit(value)

        if value != 0:
            self.coinService.storePersistentCreditValue(self.credit)

        self.checkCoinLockLevel()

    def setCoinSettings(self, coinSettings, coinLockLevel):
        self.coinSettings = coinSettings
        self.coinLockLevel = coinLockLevel

    def checkCoinLockLevel(self):
        if self.credit >= self.coinLockLevel:
            self.coinService.lockCoinMachine(True)
        else:
            self.coinService.lockCoinMachine(False)

    def getCoinSettings(self):
        return self.coinSettings

    def clearCredit(self):
        LoggingService.getLogger().info("Clear credit")
        self.bonusCounter.resetNewCurrency()
        self.changeCredit(-1 * self.credit)
        self.creditCleared.emit()

    def getCredit(self):
        return self.credit

    def getBluetoothRepresentation(self):
        return CreditBluetoothRepresentation(self)

    def getSongsRepresentation(self):
        return CreditSongRepresentation(self)

    def getCoinService(self):
        return self.coinService

    def cleanup(self):
        pass
