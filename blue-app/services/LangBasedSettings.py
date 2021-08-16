from PyQt5 import QtGui
from PyQt5 import QtCore

from services.AppSettings import AppSettings
from services import PathSettings

import os

class LangBasedSettings:

    @staticmethod
    def existMagentoTheme():
        return ThemeManager.existMagentoTheme()

    @staticmethod
    def getLangBasedQssString(lang=None):
        if not lang:
            lang = AppSettings.actualLanguage()
        styleFile = ""
        if lang == AppSettings.LanguageList[1]:
            styleFile = ":/dynamic-images/HU/fortune-style.qss"
        elif lang == AppSettings.LanguageList[0]:
            styleFile = ":/dynamic-images/EN/fortune-style.qss"
        else:
            styleFile = ":/dynamic-images/SK/fortune-style.qss"

        if LangBasedSettings.existMagentoTheme():
            styleFile = styleFile.replace("style", "style-brick")

        return QtCore.QFile(styleFile)

    @staticmethod
    def getCurrBasedCoinImage():
        if LangBasedSettings.existMagentoTheme():
            return QtGui.QPixmap(":/dynamic-images/magento-coin.png")
        currency = AppSettings.actualCurrency()
        if currency == AppSettings.CurrencyList[1]:
            return QtGui.QPixmap(":/dynamic-images/HU/coin.png")

        return QtGui.QPixmap(":/dynamic-images/SK/coin.png")


class ThemeManager:

    @staticmethod
    def existMagentoTheme():
        return os.path.exists(PathSettings.AppBasePath() + "magento-theme")

    @staticmethod
    def selectedGenreStyle():
        if ThemeManager.existMagentoTheme():
            return """
                background-color: rgba(45, 96, 97, 100%);
                border: 3px solid #26BFB6;
                border-radius: 15;
                font-size: 20px;
                color: #ba4dc7;
                """

        return """
            background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #f70202, stop: 1 #430909);
            border: 2px solid white;
            border-radius: 15;
            font-size: 18px;
            color: white;
            """

    @staticmethod
    def inactiveGenreStyle():
        if ThemeManager.existMagentoTheme():
            return """
                background-color: rgba(45, 96, 97, 65%);
                border-top: 3px solid #26BFB6;
                border-bottom: 3px solid #26BFB6;
                font-size: 16px;
                color: #FFBD00;
                """
        return """
            background-color: rgba(0, 0, 0, 65%);
            border-top: 2px solid #ABABAB;
            border-bottom: 2px solid #ABABAB;
            font-size: 16px;
            color: white;
            """
