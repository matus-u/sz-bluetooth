from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtCore

import os

from services import PathSettings

class AppSettingsNotifier(QtCore.QObject):

    moneyServerChanged = QtCore.pyqtSignal(str)
    deviceNameChanged = QtCore.pyqtSignal(str)
    servicePhoneChanged = QtCore.pyqtSignal(str)
    currencyChanged = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()

class CurrencyEur:
    def toString(value):
        return '%.2f' % value

    def longStringCorrectSpelling():
        return "eur"

    def longString():
        return "eur"

    def shortString():
        return "eur"

    def bonusThreshold():
        return 1

class CurrencyHuf:
    def toString(value):
        return '%.0f' % value

    def longString():
        return "forint"

    def longStringCorrectSpelling():
        return "forintot"

    def shortString():
        return "Ft"

    def bonusThreshold():
        return 200

class CoinSettingsIndexes:
    COIN_1 = 0
    COIN_2 = 1
    COIN_3 = 2
    COIN_4 = 3
    COIN_5 = 4
    COIN_6 = 5
    CPP_VALUE = 6
    MINUTE_COST_VALUE = 7
    SONG_COST_VALUE = 8
    MONEY_BLUETOOTH_OVERTAKING_VALUE = 9

class AppSettings:
    SettingsPath = PathSettings.AppBasePath() + "../blue-app-configs/blue-app.conf"
    SettingsFormat = QtCore.QSettings.NativeFormat
    TimeZoneList = ["UTC","Europe/Budapest","Europe/Bratislava","Europe/London"]
    LanguageList = ["english","hungarian","slovak","polish"]
    LanguageString = "language"
    TimeZoneString = "timezone"
    AvailableLanguagesListString = "availableLanguages"
    Translator = QtCore.QTranslator()

    CurrencyList = ["EUR","HUF"]
    CurrencyString = "currency"

    WirelessSettingsPath = PathSettings.AppBasePath() + "../blue-app-configs/wireless.conf"
    WirelessEnabledString = "Enabled"
    SSIDString = "SSID"
    WirelessPassString = "WirelessPass"

    CoinValuesString = "coin-settings"
    DefaultCoinValues = { "EUR" : [0,0,0.5,1,2,0,1,0.05,0.50,0.50], "HUF" : [100,200,0,0,0,0,500,10,100,100] }

    AppVersion = "UNKNOWN"
    DeviceNameString = "DeviceName"
    OwnerString = "Owner"
    ServicePhoneString = "ServicePhone"
    DescString = "Description"
    MoneyServerString = "MoneyServer"
    InkeeperPercentileString = "InkeeperPercentile"

    ViewTypeString = "ViewType"
    ViewTypeList = ["Genre based","Alphabetical"]

    GenreIteratingString = "GenreIterating"
    GenreIteratingList = ["Type 1","Type 2"]

    BluetoothEnabledString = "BluetoothEnabled"
    SongTimeVisString = "SongTimesVisible"
    CoinLockLevel = "CoinLockLevel"

    VolumeAtStartString = "VolumeAtStart"
    SystemSoundVolumeLevelString = "SystemSoundVolumeLevel"

    Notifier = AppSettingsNotifier()


    @staticmethod
    def checkSettingsMap(settings, path):
        if settings is not None:
            return settings
        else:
            return QtCore.QSettings(path, AppSettings.SettingsFormat)

    @staticmethod
    def checkSettingsParam(settings):
        return AppSettings.checkSettingsMap(settings, AppSettings.SettingsPath)

    @staticmethod
    def checkWifiSettingsParam(settings):
        return AppSettings.checkSettingsMap(settings, AppSettings.WirelessSettingsPath)

    @staticmethod
    def actualAppVersion():
        try:
            f = open("scripts/version", "r")
            return f.read().strip()
        except:
            return AppSettings.AppVersion

    @staticmethod
    def actualAvailableLanguages(appSettings = None):
        return AppSettings.checkSettingsParam(appSettings).value(AppSettings.AvailableLanguagesListString, AppSettings.LanguageList)

    @staticmethod
    def actualLanguage(appSettings = None):
        return AppSettings.checkSettingsParam(appSettings).value(AppSettings.LanguageString, AppSettings.LanguageList[0])

    @staticmethod
    def getCurrentLanguageIndex():
        return AppSettings.actualAvailableLanguages().index(AppSettings.actualLanguage())

    @classmethod
    def restoreLanguage(cls):
        cls._loadLanguage(AppSettings.actualLanguage())

    @classmethod
    def restoreTimeZone(cls):
        QtCore.QProcess.execute("scripts/set-time-zone.sh", [AppSettings.actualTimeZone()])

    @staticmethod
    def actualTimeZone(appSettings = None):
        return AppSettings.checkSettingsParam(appSettings).value(AppSettings.TimeZoneString, AppSettings.TimeZoneList[0])

    @staticmethod
    def getCurrentTimeZoneIndex():
        return AppSettings.TimeZoneList.index(AppSettings.actualTimeZone())

    @staticmethod
    def actualCurrency(appSettings = None):
        return AppSettings.checkSettingsParam(appSettings).value(AppSettings.CurrencyString, AppSettings.CurrencyList[0])

    @staticmethod
    def getCurrentCurrencyIndex():
        return AppSettings.CurrencyList.index(AppSettings.actualCurrency())

    @staticmethod
    def actualViewType(appSettings = None):
        return AppSettings.checkSettingsParam(appSettings).value(AppSettings.ViewTypeString, AppSettings.ViewTypeList[0])

    @staticmethod
    def actualGenreIteratingType(appSettings = None):
        return AppSettings.checkSettingsParam(appSettings).value(AppSettings.GenreIteratingString, AppSettings.GenreIteratingList[0])

    @staticmethod
    def getCurrentViewTypeIndex():
        return AppSettings.ViewTypeList.index(AppSettings.actualViewType())

    @staticmethod
    def getCurrentGenreIteratingTypeIndex():
        return AppSettings.GenreIteratingList.index(AppSettings.actualGenreIteratingType())

    @staticmethod
    def actualSongTimeVisible(appSettings = None):
        return AppSettings.checkSettingsParam(appSettings).value(AppSettings.SongTimeVisString, True, bool)

    @staticmethod
    def actualBluetoothEnabled(appSettings = None):
        return AppSettings.checkSettingsParam(appSettings).value(AppSettings.BluetoothEnabledString, True, bool)

    @staticmethod
    def actualCoinSettings(appSettings = None):
        default = AppSettings.DefaultCoinValues[AppSettings.actualCurrency()]
        value = AppSettings.checkSettingsParam(appSettings).value(AppSettings.CoinValuesString, [], float)
        value.extend(default[len(value):])
        return value

    @staticmethod
    def actualInkeeperPercentile(appSettings = None):
        return AppSettings.checkSettingsParam(appSettings).value(AppSettings.InkeeperPercentileString, 0, int)

    @staticmethod
    def actualVolumeAtStart(appSettings = None):
        return AppSettings.checkSettingsParam(appSettings).value(AppSettings.VolumeAtStartString, 30, int)

    @staticmethod
    def actualSystemSoundVolumeLevel(appSettings = None):
        return AppSettings.checkSettingsParam(appSettings).value(AppSettings.SystemSoundVolumeLevelString, 50, int)

    @staticmethod
    def defaultCoinSettings(currency):
        return AppSettings.DefaultCoinValues[currency]

    @staticmethod
    def defaultCoinLockLevel(currency):
        defaultCoinLevel = 0.0
        if currency == "EUR":
            defaultCoinLevel = 4.0

        if currency == "HUF":
            defaultCoinLevel = 1000
        return defaultCoinLevel

    @staticmethod
    def actualCoinLockLevel(appSettings = None):
        return AppSettings.checkSettingsParam(appSettings).value(AppSettings.CoinLockLevel, AppSettings.defaultCoinLockLevel(AppSettings.actualCurrency(appSettings)), float)

    @staticmethod
    def currencyStringByIndex(index):
        return AppSettings.CurrencyList[index]

    @staticmethod
    def currencyClass():
        currency = AppSettings.actualCurrency()
        if currency == "HUF":
            return CurrencyHuf
        return CurrencyEur

    @classmethod
    def _loadLanguage(cls, language):
        app = QtWidgets.QApplication.instance()
        app.removeTranslator(cls.Translator)
        cls.Translator = QtCore.QTranslator()
        cls.Translator.load(language + ".qm", "./translation")
        app.installTranslator(cls.Translator)
        QtCore.QCoreApplication.processEvents()

    @classmethod
    def storeLanguage(cls, language):
        settings = QtCore.QSettings(AppSettings.SettingsPath, AppSettings.SettingsFormat)
        settings.setValue(AppSettings.LanguageString, language)

    @classmethod
    def resetMoneyRelatedSettings(cls):
        settings = QtCore.QSettings(AppSettings.SettingsPath, AppSettings.SettingsFormat)
        currency = AppSettings.actualCurrency()
        settings.setValue(AppSettings.InkeeperPercentileString, 0)
        settings.setValue(AppSettings.CoinValuesString, AppSettings.defaultCoinSettings(currency))
        settings.setValue(AppSettings.CoinLockLevel, AppSettings.defaultCoinLockLevel(currency))
        settings.sync()

    @classmethod
    def storeSettings(cls, language, availableLanguages, timeZoneIndex, currencyIndex, coinSettingsList, moneyServer, bluetoothEnabled, songTimeVisEnabled, viewTypeIndex, genreIteratingIndex, coinLockLevel, inkeeperPercentile, volumeAtStart, systemSoundVolumeLevel):
        settings = QtCore.QSettings(AppSettings.SettingsPath, AppSettings.SettingsFormat)
        settings.setValue(AppSettings.LanguageString, language)
        settings.setValue(AppSettings.AvailableLanguagesListString, availableLanguages)
        settings.setValue(AppSettings.TimeZoneString, AppSettings.TimeZoneList[timeZoneIndex])

        if AppSettings.CurrencyList[currencyIndex] != AppSettings.actualCurrency(settings):
            settings.setValue(AppSettings.CurrencyString, AppSettings.CurrencyList[currencyIndex])
            cls.getNotifier().currencyChanged.emit(AppSettings.CurrencyList[currencyIndex])

        settings.setValue(AppSettings.CoinValuesString, coinSettingsList)
        settings.setValue(AppSettings.CoinLockLevel, coinLockLevel)

        if moneyServer != AppSettings.actualMoneyServer(settings):
            settings.setValue(AppSettings.MoneyServerString, moneyServer)
            cls.getNotifier().moneyServerChanged.emit(moneyServer)

        settings.setValue(AppSettings.ViewTypeString, AppSettings.ViewTypeList[viewTypeIndex])
        settings.setValue(AppSettings.GenreIteratingString, AppSettings.GenreIteratingList[genreIteratingIndex])
        settings.setValue(AppSettings.SongTimeVisString, songTimeVisEnabled)
        settings.setValue(AppSettings.BluetoothEnabledString, bluetoothEnabled)
        settings.setValue(AppSettings.InkeeperPercentileString, inkeeperPercentile)
        settings.setValue(AppSettings.VolumeAtStartString, volumeAtStart)
        settings.setValue(AppSettings.SystemSoundVolumeLevelString, systemSoundVolumeLevel)

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
    def actualWirelessEnabled(appSettings = None):
        return AppSettings.checkWifiSettingsParam(appSettings).value(AppSettings.WirelessEnabledString, False, bool)

    @staticmethod
    def actualWirelessSSID(appSettings = None):
        return AppSettings.checkWifiSettingsParam(appSettings).value(AppSettings.SSIDString, "")

    @staticmethod
    def actualWirelessPassword(appSettings = None):
        return AppSettings.checkWifiSettingsParam(appSettings).value(AppSettings.WirelessPassString, "")

    @staticmethod
    def actualDeviceName(appSettings = None):
        return AppSettings.checkSettingsParam(appSettings).value(AppSettings.DeviceNameString, "")

    @staticmethod
    def actualOwner(appSettings = None):
        return AppSettings.checkSettingsParam(appSettings).value(AppSettings.OwnerString, "")

    @staticmethod
    def actualDescription(appSettings = None):
        return AppSettings.checkSettingsParam(appSettings).value(AppSettings.DescString, "")

    @staticmethod
    def actualServicePhone(appSettings = None):
        return AppSettings.checkSettingsParam(appSettings).value(AppSettings.ServicePhoneString, "")

    @staticmethod
    def actualMoneyServer(appSettings = None):
        return AppSettings.checkSettingsParam(appSettings).value(AppSettings.MoneyServerString, "")

    @classmethod
    def storeServerSettings(cls, name, owner, desc, servicePhone):
        settings = QtCore.QSettings(AppSettings.SettingsPath, AppSettings.SettingsFormat)
        if name is not None:
            if name != AppSettings.actualDeviceName(settings):
                settings.setValue(AppSettings.DeviceNameString, name)
                cls.getNotifier().deviceNameChanged.emit(name)
        if owner is not None:
            settings.setValue(AppSettings.OwnerString, owner)
        if desc is not None:
            settings.setValue(AppSettings.DescString, desc)
        if servicePhone is not None:
            if servicePhone != AppSettings.actualServicePhone(settings):
                settings.setValue(AppSettings.ServicePhoneString, servicePhone)
                cls.getNotifier().servicePhoneChanged.emit(servicePhone)
        settings.sync()

    @classmethod
    def getNotifier(cls):
        return cls.Notifier


    @staticmethod
    def applySystemSoundVolumeLevel():
        os.system("amixer sset 'SoftSoundMaster' {}%".format(AppSettings.actualSystemSoundVolumeLevel()))

