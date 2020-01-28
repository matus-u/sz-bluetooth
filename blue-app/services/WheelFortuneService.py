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

        self.settings = QtCore.QSettings(WheelFortuneService.SettingsPath, WheelFortuneService.SettingsFormat)

    def setSettings(self, enabled, moneyLevel):
        self.settings.setValue(WheelFortuneService.Enabled, enabled)
        self.settings.setValue(WheelFortuneService.MoneyLevel, moneyLevel)

    def isEnabled(self):
        return self.settings.value(WheelFortuneService.Enabled, False, bool)

    def moneyLevel(self):
        return self.settings.value(WheelFortuneService.MoneyLevel, 0.0, float)

