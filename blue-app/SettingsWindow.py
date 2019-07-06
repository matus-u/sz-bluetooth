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
        self.ui.languageCombobox.currentIndexChanged.connect(self.onLanguageComboboxChanged)

    def onLanguageComboboxChanged(self, index):
        AppSettings.loadLanguageByIndex(index)

    def onOkButton(self):
        AppSettings.storeSettings(self.ui.languageCombobox.currentIndex(), self.ui.timeZoneCombobox.currentIndex())
        self.accept()

    def onCancelButton(self):
        AppSettings.restoreLanguage()
        self.reject()

    def changeEvent(self, event):
        if event.type() == QtCore.QEvent.LanguageChange:
            self.ui.retranslateUi(self)
        super(SettingsWindow, self).changeEvent(event)
