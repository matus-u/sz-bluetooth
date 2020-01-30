from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

class WheelFortuneService(QtCore.QObject):
    SettingsPath = "../blue-app-configs/wheel-fortune.conf"
    SettingsFormat = QtCore.QSettings.NativeFormat

    Enabled = "Enabled"
    MoneyLevel = "MoneyLevel"

    def __init__(self):
        super().__init__()

        self.counter = 0.0
        self.settings = QtCore.QSettings(WheelFortuneService.SettingsPath, WheelFortuneService.SettingsFormat)

        self.probabilityValues = {}

    def setSettings(self, enabled, moneyLevel):
        if (self.isEnabled() != enabled) or (moneyLevel != self.moneyLevel()):
            self.counter = 0.0
        self.settings.setValue(WheelFortuneService.Enabled, enabled)
        self.settings.setValue(WheelFortuneService.MoneyLevel, moneyLevel)

    def isEnabled(self):
        return self.settings.value(WheelFortuneService.Enabled, False, bool)

    def moneyLevel(self):
        return self.settings.value(WheelFortuneService.MoneyLevel, 0.0, float)

    def moneyInserted(self, money):
        if self.isEnabled():
            mLevel = self.moneyLevel()
            self.counter = round (self.counter + round(money, 2), 2)

            while (self.counter >= mLevel):
                self.counter = self.counter - self.moneyLevel()
                self.tryWin()

    def setNewProbabilityValues(self, values):
        self.probabilityValues = values
        print (values)

    def tryWin(self):
        print ("TRY WIN")

