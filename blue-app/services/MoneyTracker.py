from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

class MoneyTracker(QtCore.QObject):
    SettingsPath = "../blue-app-configs/money-tracking.conf"
    SettingsFormat = QtCore.QSettings.NativeFormat

    FromLastWithdrawCounter = "FromLastWithdrawCounter"
    TotalCounter = "TotalCounter"

    FROM_LAST_WITHDRAW_COUNTER_INDEX = 0
    TOTAL_COUNTER_INDEX = 1

    def __init__(self):
        super().__init__()

        self.settings = QtCore.QSettings(MoneyTracker.SettingsPath, MoneyTracker.SettingsFormat)

    def addToCounters(self, money):
        fromLastWithdrawCounter = self.settings.value(MoneyTracker.FromLastWithdrawCounter, 0.0, float)
        totalCounter = self.settings.value(MoneyTracker.TotalCounter, 0.0, float)
        self.settings.setValue(MoneyTracker.FromLastWithdrawCounter, fromLastWithdrawCounter + money)
        self.settings.setValue(MoneyTracker.TotalCounter, totalCounter + money)
        #self.settings.sync()

    def withdraw(self):
        self.settings.setValue(MoneyTracker.FromLastWithdrawCounter, 0.0)
        self.settings.sync()

    def resetAllCounters(self):
        self.settings.setValue(MoneyTracker.TotalCounter, 0.0)
        self.settings.setValue(MoneyTracker.FromLastWithdrawCounter, 0.0)
        self.settings.sync()

    def getCounters(self):
        return [self.settings.value(MoneyTracker.FromLastWithdrawCounter, 0.0, float), self.settings.value(MoneyTracker.TotalCounter, 0.0, float) ]


