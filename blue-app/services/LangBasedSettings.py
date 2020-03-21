from PyQt5 import QtGui
from PyQt5 import QtCore

from services.AppSettings import AppSettings

class LangBasedSettings:
    def __init__(self):
        self.lang = None
        self.reloadLanguage()

    def reloadLanguage(self):
        self.lang = AppSettings.actualLanguage()

    def getLangBasedQssString(self):
        if (self.lang) == AppSettings.LanguageList[1]:
            return QtCore.QFile(":/dynamic-images/HU/fortune-style.qss")

        return QtCore.QFile(":/dynamic-images/SK/fortune-style.qss")

    def getLangBasedCoinImage(self):
        if (self.lang) == AppSettings.LanguageList[1]:
            return QtGui.QPixmap(":/dynamic-images/HU/coin.png")

        return QtGui.QPixmap(":/dynamic-images/SK/coin.png")
