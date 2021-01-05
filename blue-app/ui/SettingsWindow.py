from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from generated.Settings import Ui_Settings

from services.AppSettings import AppSettings
from ui import WaitUserWindow

class SettingsWindow(QtWidgets.QDialog):
    def __init__(self, parent, moneyTracker, fortuneService, creditService):
        super(SettingsWindow, self).__init__(parent)
        self.ui = Ui_Settings()
        self.ui.setupUi(self)
        self.moneyTracker = moneyTracker
        self.fortuneService = fortuneService
        self.creditService = creditService

        self.ui.okButton.clicked.connect(self.onOkButton)
        self.ui.cancelButton.clicked.connect(self.onCancelButton)
        self.ui.timeZoneCombobox.setCurrentIndex(AppSettings.getCurrentTimeZoneIndex())
        self.ui.currencyCombobox.setCurrentIndex(AppSettings.getCurrentCurrencyIndex())
        self.ui.languageCombobox.currentIndexChanged.connect(self.onLanguageComboboxChanged)
        self.ui.currencyCombobox.currentIndexChanged.connect(lambda index: self.setCoinSettings(AppSettings.defaultCoinSettings(AppSettings.currencyStringByIndex(index))))
        self.ui.moneyServerAddress.setText(AppSettings.actualMoneyServer())
        self.ui.viewTypeComboBox.setCurrentIndex(AppSettings.getCurrentViewTypeIndex())
        self.ui.genreIteratingComboBox.setCurrentIndex(AppSettings.getCurrentGenreIteratingTypeIndex())
        self.ui.songTimeCheckBox.setChecked(AppSettings.actualSongTimeVisible())
        self.ui.bluetoothEnabledCheckBox.setChecked(AppSettings.actualBluetoothEnabled())
        self.setCoinSettings(AppSettings.actualCoinSettings())
        self.ui.coinLockLevel.setValue(AppSettings.actualCoinLockLevel())

        availableLanguages = AppSettings.actualAvailableLanguages()
        allLanguageList = AppSettings.LanguageList
        self.ui.availableLanguagesWidget.setRowCount(len(allLanguageList))
        row = 0
        self.checkBoxes = []
        for language in allLanguageList:
            checkBox = QtWidgets.QCheckBox(language, self)
            checkBox.setChecked(language in availableLanguages)
            checkBox.stateChanged.connect(lambda state: self.rePopulageLanguageCombobox())
            self.checkBoxes.append(checkBox)
            self.ui.availableLanguagesWidget.setCellWidget(row,0, checkBox)
            row = row+1

        self.ui.languageCombobox.clear()
        self.ui.languageCombobox.addItems(availableLanguages)
        self.ui.languageCombobox.setEditable(False)
        self.ui.languageCombobox.setCurrentText(AppSettings.actualLanguage())
        self.enableCheckBoxes()
        self.waitUserWindow = WaitUserWindow.WaitUserWindow(self)

    def rePopulageLanguageCombobox(self):
        currentLang = self.ui.languageCombobox.currentText()

        self.ui.languageCombobox.clear()
        for checkBox in self.checkBoxes:
            if checkBox.isChecked():
                self.ui.languageCombobox.addItem(checkBox.text())
        self.ui.languageCombobox.setEditable(False)
        self.ui.languageCombobox.setCurrentText(currentLang)
        self.enableCheckBoxes()

    def enableCheckBoxes(self):
        for checkBox in self.checkBoxes:
            if (checkBox.text() == self.ui.languageCombobox.currentText()):
                checkBox.setEnabled(False)
            else:
                checkBox.setEnabled(True)

    def onCheckBoxChange(self, checkbox, state):
        self.enableCheckBoxes()

    def setCoinSettings(self,coinSettings):
        self.ui.coin1value.setValue(coinSettings[0])
        self.ui.coin2value.setValue(coinSettings[1])
        self.ui.coin3value.setValue(coinSettings[2])
        self.ui.coin4value.setValue(coinSettings[3])
        self.ui.coin5value.setValue(coinSettings[4])
        self.ui.coin6value.setValue(coinSettings[5])
        self.ui.cppValue.setValue(coinSettings[6])
        self.ui.secondCostsValue.setValue(coinSettings[7])
        self.ui.songCostsValue.setValue(coinSettings[8])

    def getCoinSettingsFromUi(self):
        return [
            self.ui.coin1value.value(),
            self.ui.coin2value.value(),
            self.ui.coin3value.value(),
            self.ui.coin4value.value(),
            self.ui.coin5value.value(),
            self.ui.coin6value.value(),
            self.ui.cppValue.value(),
            self.ui.secondCostsValue.value(),
            self.ui.songCostsValue.value()
        ]

    def onLanguageComboboxChanged(self, index):
        AppSettings._loadLanguage(self.ui.languageCombobox.currentText())
        self.enableCheckBoxes()

    def onOkButton(self):
        if AppSettings.actualCurrency() != AppSettings.currencyStringByIndex(self.ui.currencyCombobox.currentIndex()):
            shouldChangeCurrency = QtWidgets.QMessageBox.question(self, self.tr("Currency has changed!"), self.tr("Changing currency resets all internal money counters, proceed?"))
            if shouldChangeCurrency == QtWidgets.QMessageBox.Yes:

                shouldChangeCurrency = QtWidgets.QMessageBox.question(self, self.tr("Currency is goin to change!"), self.tr("Proceed?"))
                if shouldChangeCurrency == QtWidgets.QMessageBox.Yes:
                    self.moneyTracker.resetAllCounters()
                    self.creditService.clearCredit()
                    self.fortuneService.resetActualFortuneTryLevels()
                else:
                    return
            else:
                return

        QtCore.QTimer.singleShot(500, self.onOkWork)
        self.waitUserWindow.exec()

    def onOkWork(self):
        AppSettings.storeSettings(self.ui.languageCombobox.currentText(),
                                  [self.ui.languageCombobox.itemText(i) for i in range(self.ui.languageCombobox.count())],
                                  self.ui.timeZoneCombobox.currentIndex(),
                                  self.ui.currencyCombobox.currentIndex(),
                                  self.getCoinSettingsFromUi(),
                                  self.ui.moneyServerAddress.text(),
                                  self.ui.bluetoothEnabledCheckBox.isChecked(),
                                  self.ui.songTimeCheckBox.isChecked(),
                                  self.ui.viewTypeComboBox.currentIndex(),
                                  self.ui.genreIteratingComboBox.currentIndex(),
                                  self.ui.coinLockLevel.value()
                                  )
        self.accept()
        self.waitUserWindow.accept()

    def onCancelButton(self):
        AppSettings.restoreLanguage()
        self.reject()

    def changeEvent(self, event):
        if event.type() == QtCore.QEvent.LanguageChange:
            self.ui.retranslateUi(self)
        super(SettingsWindow, self).changeEvent(event)
