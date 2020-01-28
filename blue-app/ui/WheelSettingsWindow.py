from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

from generated.WheelSettings import Ui_WheelSettings
from services.WheelFortuneService import WheelFortuneService

class WheelSettingsWindow(QtWidgets.QDialog):
    def __init__(self, parent, wheelFortuneService):
        super(WheelSettingsWindow, self).__init__(parent)
        self.ui = Ui_WheelSettings()
        self.ui.setupUi(self)
        self.service = wheelFortuneService

        self.ui.okButton.clicked.connect(self.onOkButton)
        self.ui.cancelButton.clicked.connect(self.reject)

        self.ui.fortuneCheckBox.toggled.connect(lambda state: self.ui.moneySpinBox.setEnabled(state))
        self.ui.fortuneCheckBox.setChecked(self.service.isEnabled())
        self.ui.moneySpinBox.setValue(self.service.moneyLevel())

    def onOkButton(self):
        self.service.setSettings(self.ui.fortuneCheckBox.isChecked(), self.ui.moneySpinBox.value())
        self.accept()
