from PyQt5 import QtGui
from PyQt5 import QtCore

from services.AppSettings import AppSettings

class LangBasedSettings:

    @staticmethod
    def getLangBasedQssString(lang=None):
        if not lang:
            lang = AppSettings.actualLanguage()
        if lang == AppSettings.LanguageList[1]:
            return QtCore.QFile(":/dynamic-images/HU/fortune-style.qss")
        if lang == AppSettings.LanguageList[0]:
            return QtCore.QFile(":/dynamic-images/EN/fortune-style.qss")

        return QtCore.QFile(":/dynamic-images/SK/fortune-style.qss")

    @staticmethod
    def getCurrBasedCoinImage():
        currency = AppSettings.actualCurrency()
        if currency == AppSettings.CurrencyList[1]:
            return QtGui.QPixmap(":/dynamic-images/HU/coin.png")

        return QtGui.QPixmap(":/dynamic-images/SK/coin.png")
