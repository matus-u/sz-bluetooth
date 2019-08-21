from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore


class AppSettings:
    SettingsPath = "configs/blue-app.conf"
    SettingsFormat = QtCore.QSettings.NativeFormat
    TimeZoneList = ["UTC","Europe/Budapest","Europe/Bratislava","Europe/London"]
    LanguageList = ["english","hungarian","slovak"]
    LanguageString = "language"
    TimeZoneString = "timezone"
    Translator = QtCore.QTranslator()

    CurrencyList = ["EUR","HUF"]
    CurrencyString = "currency"

    WirelessSettingsPath = "configs/wireless.conf"
    WirelessEnabledString = "Enabled"
    SSIDString = "SSID"
    WirelessPassString = "WirelessPass"

    CoinValuesString = "coin-settings"
    DefaultCoinValues = { "EUR" : [0,0.5,1,2,0,0,1,0.01], "HUF" : [0,0,0,0,100,200,500,10] }

    @staticmethod
    def actualLanguage():
        return QtCore.QSettings(AppSettings.SettingsPath, AppSettings.SettingsFormat).value(AppSettings.LanguageString, AppSettings.LanguageList[0])

    @staticmethod
    def getCurrentLanguageIndex():
        return AppSettings.LanguageList.index(AppSettings.actualLanguage())

    @classmethod
    def restoreLanguage(cls):
        cls._loadLanguage(AppSettings.actualLanguage())

    @staticmethod
    def actualTimeZone():
        return QtCore.QSettings(AppSettings.SettingsPath, AppSettings.SettingsFormat).value(AppSettings.TimeZoneString, AppSettings.TimeZoneList[0])

    @staticmethod
    def getCurrentTimeZoneIndex():
        return AppSettings.TimeZoneList.index(AppSettings.actualTimeZone())

    @classmethod
    def loadLanguageByIndex(cls, index):
        cls._loadLanguage(AppSettings.LanguageList[index])

    @staticmethod
    def actualCurrency():
        return QtCore.QSettings(AppSettings.SettingsPath, AppSettings.SettingsFormat).value(AppSettings.CurrencyString, AppSettings.CurrencyList[0])

    @staticmethod
    def getCurrentCurrencyIndex():
        return AppSettings.CurrencyList.index(AppSettings.actualCurrency())

    @staticmethod
    def actualCoinSettings():
        return QtCore.QSettings(AppSettings.SettingsPath, AppSettings.SettingsFormat).value(AppSettings.CoinValuesString, AppSettings.DefaultCoinValues[AppSettings.actualCurrency()], float)

    @staticmethod
    def defaultCoinSettings(currency):
        return AppSettings.DefaultCoinValues[currency]

    @staticmethod
    def currencyStringByIndex(index):
        return AppSettings.CurrencyList[index]

    @classmethod
    def _loadLanguage(cls, language):
        app = QtWidgets.QApplication.instance()
        app.removeTranslator(cls.Translator)
        cls.Translator = QtCore.QTranslator()
        cls.Translator.load(language + ".qm", "./translation")
        app.installTranslator(cls.Translator)
        QtCore.QCoreApplication.processEvents()

    @classmethod
    def storeSettings(cls, languageIndex, timeZoneIndex, currencyIndex, coinSettingsList):
        settings = QtCore.QSettings(AppSettings.SettingsPath, AppSettings.SettingsFormat)
        settings.setValue(AppSettings.LanguageString, AppSettings.LanguageList[languageIndex])
        settings.setValue(AppSettings.TimeZoneString, AppSettings.TimeZoneList[timeZoneIndex])
        settings.setValue(AppSettings.CurrencyString, AppSettings.CurrencyList[currencyIndex])
        settings.setValue(AppSettings.CoinValuesString, coinSettingsList)
        settings.sync()
        QtCore.QProcess.execute("scripts/set-time-zone.sh", [AppSettings.TimeZoneList[timeZoneIndex]])


    @classmethod
    def storeWirelessSettings(cls, enabled, SSID, password):
        settings = QtCore.QSettings(AppSettings.WirelessSettingsPath, AppSettings.SettingsFormat)
        settings.setValue(AppSettings.WirelessEnabledString, enabled)
        settings.setValue(AppSettings.SSIDString, SSID)
        settings.setValue(AppSettings.WirelessPassString, password)
        settings.sync()

    @staticmethod
    def actualWirelessEnabled():
        return QtCore.QSettings(AppSettings.WirelessSettingsPath, AppSettings.SettingsFormat).value(AppSettings.WirelessEnabledString, False, bool)

    @staticmethod
    def actualWirelessSSID():
        return QtCore.QSettings(AppSettings.WirelessSettingsPath, AppSettings.SettingsFormat).value(AppSettings.SSIDString, "")

    @staticmethod
    def actualWirelessPassword():
        return QtCore.QSettings(AppSettings.WirelessSettingsPath, AppSettings.SettingsFormat).value(AppSettings.WirelessPassString, "")

