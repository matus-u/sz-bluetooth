from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

from services.LoggingService import LoggingService
from datetime import date, timedelta
from services import PathSettings

class MoneyTracker(QtCore.QObject):
    SettingsPath = PathSettings.AppBasePath() + "../blue-app-configs/money-tracking.conf"
    SettingsFormat = QtCore.QSettings.NativeFormat

    FromLastWithdrawCounter = "FromLastWithdrawCounter"
    TotalCounter = "TotalCounter"
    LastWithdrawDate = "LastWithdrawDate"

    FROM_LAST_WITHDRAW_COUNTER_INDEX = 0
    TOTAL_COUNTER_INDEX = 1

    PreviousGain = "PreviousGain"
    ActualGain = "ActualGain"

    PreviousDate = "PreviousDate"
    ActualDate = "ActualDate"

    def __init__(self):
        super().__init__()

        self.settings = QtCore.QSettings(MoneyTracker.SettingsPath, MoneyTracker.SettingsFormat)
        self.updateGainData()
        self.checkGainsDataTimer = QtCore.QTimer()
        self.checkGainsDataTimer.timeout.connect(self.updateGainData)
        self.checkGainsDataTimer.start(1000*60*60*12)

    def updateGainData(self):
        actualDate = self.settings.value(MoneyTracker.ActualDate, "")
        today = str(date.today())
        yesterday = str(date.today() - timedelta(days=1))

        if (today != actualDate):
            if yesterday == actualDate:
                self.settings.setValue(MoneyTracker.PreviousGain, self.settings.value(MoneyTracker.ActualGain, 0.0, float))
                self.settings.setValue(MoneyTracker.ActualGain, 0.0)
                self.settings.setValue(MoneyTracker.PreviousDate, self.settings.value(MoneyTracker.ActualDate, ""))
                self.settings.setValue(MoneyTracker.ActualDate, today)
            else:
                self.settings.setValue(MoneyTracker.PreviousGain, 0.0)
                self.settings.setValue(MoneyTracker.ActualGain, 0.0)
                self.settings.setValue(MoneyTracker.PreviousDate, "")
                self.settings.setValue(MoneyTracker.ActualDate, today)

    def addToCounters(self, money):
        self.updateGainData()
        fromLastWithdrawCounter = self.settings.value(MoneyTracker.FromLastWithdrawCounter, 0.0, float)
        totalCounter = self.settings.value(MoneyTracker.TotalCounter, 0.0, float)
        self.settings.setValue(MoneyTracker.FromLastWithdrawCounter, fromLastWithdrawCounter + money)
        self.settings.setValue(MoneyTracker.TotalCounter, totalCounter + money)
        self.settings.setValue(MoneyTracker.ActualGain, self.settings.value(MoneyTracker.ActualGain, 0.0, float) + money)
        #self.settings.sync()

    def withdraw(self):
        LoggingService.getLogger().info("Widthraw money " + str(self.getCounters()))
        self.settings.setValue(MoneyTracker.FromLastWithdrawCounter, 0.0)
        self.settings.setValue(MoneyTracker.LastWithdrawDate, str(date.today()))
        self.settings.sync()

    def resetAllCounters(self):
        LoggingService.getLogger().info("Reset all counters")
        self.settings.setValue(MoneyTracker.TotalCounter, 0.0)
        self.settings.setValue(MoneyTracker.FromLastWithdrawCounter, 0.0)
        self.settings.setValue(MoneyTracker.LastWithdrawDate, "")
        self.settings.setValue(MoneyTracker.PreviousGain, 0.0)
        self.settings.setValue(MoneyTracker.ActualGain, 0.0)
        self.settings.setValue(MoneyTracker.PreviousDate, "")
        self.settings.setValue(MoneyTracker.ActualDate, "")
        self.settings.sync()

    def getCounters(self):
        return [self.settings.value(MoneyTracker.FromLastWithdrawCounter, 0.0, float), self.settings.value(MoneyTracker.TotalCounter, 0.0, float) ]

    def getGainData(self):
        return {
            MoneyTracker.PreviousGain : self.settings.value(MoneyTracker.PreviousGain, 0.0, float),
            MoneyTracker.ActualGain : self.settings.value(MoneyTracker.ActualGain, 0.0, float),
            MoneyTracker.PreviousDate : self.settings.value(MoneyTracker.PreviousDate, ""),
            MoneyTracker.ActualDate : self.settings.value(MoneyTracker.ActualDate, "")
        }

    def lastWithdrawDate(self):
        return self.settings.value(MoneyTracker.LastWithdrawDate, "")



