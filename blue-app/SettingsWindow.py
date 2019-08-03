from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from generated.Settings import Ui_Settings

from services.AppSettings import AppSettings

class SettingsWindow(QtWidgets.QDialog):
    def __init__(self):
        super(SettingsWindow, self).__init__()
        self.ui = Ui_Settings()
        self.ui.setupUi(self)

        self.ui.okButton.clicked.connect(self.onOkButton)
        self.ui.cancelButton.clicked.connect(self.onCancelButton)
        self.ui.languageCombobox.setCurrentIndex(AppSettings.getCurrentLanguageIndex())
        self.ui.timeZoneCombobox.setCurrentIndex(AppSettings.getCurrentTimeZoneIndex())
        self.ui.currencyCombobox.setCurrentIndex(AppSettings.getCurrentCurrencyIndex())
        self.ui.languageCombobox.currentIndexChanged.connect(self.onLanguageComboboxChanged)
        self.ui.currencyCombobox.currentIndexChanged.connect(lambda index: self.setCoinSettings(AppSettings.defaultCoinSettings(AppSettings.currencyStringByIndex(index))))
        self.setCoinSettings(AppSettings.actualCoinSettings())

    def setCoinSettings(self,coinSettings):
        self.ui.coin1value.setValue(coinSettings[0])
        self.ui.coin2value.setValue(coinSettings[1])
        self.ui.coin3value.setValue(coinSettings[2])
        self.ui.coin4value.setValue(coinSettings[3])
        self.ui.coin5value.setValue(coinSettings[4])
        self.ui.coin6value.setValue(coinSettings[5])
        self.ui.cppValue.setValue(coinSettings[6])
        self.ui.secondCostsValue.setValue(coinSettings[7])

    def getCoinSettingsFromUi(self):
        return [
            self.ui.coin1value.value(),
            self.ui.coin2value.value(),
            self.ui.coin3value.value(),
            self.ui.coin4value.value(),
            self.ui.coin5value.value(),
            self.ui.coin6value.value(),
            self.ui.cppValue.value(),
            self.ui.secondCostsValue.value()
        ]

    def onLanguageComboboxChanged(self, index):
        AppSettings.loadLanguageByIndex(index)

    def onOkButton(self):
        AppSettings.storeSettings(self.ui.languageCombobox.currentIndex(), self.ui.timeZoneCombobox.currentIndex(), self.ui.currencyCombobox.currentIndex(), self.getCoinSettingsFromUi())
        self.accept()

    def onCancelButton(self):
        AppSettings.restoreLanguage()
        self.reject()

    def changeEvent(self, event):
        if event.type() == QtCore.QEvent.LanguageChange:
            self.ui.retranslateUi(self)
        super(SettingsWindow, self).changeEvent(event)
