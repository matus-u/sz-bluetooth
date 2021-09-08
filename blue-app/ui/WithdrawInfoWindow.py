
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from generated.WithdrawInfo import Ui_WithdrawInfo

from services.LedButtonService import LedButtonService

from ui.ApplicationWindowHelpers import StandardArrowHandler
from ui import FocusHandler
from services.AppSettings import AppSettings
from datetime import datetime

class WithdrawInfoWindow(QtWidgets.QDialog):
    def __init__(self, parent, ledButtonService, arrowHandler, message, title, inventoryValues):
        super(WithdrawInfoWindow, self).__init__(parent)

        self.ui = Ui_WithdrawInfo()
        self.ui.setupUi(self)
        self.setWindowTitle(title)
        self.ui.messageLabel.setText(message)
        self.ui.withdrawOkButton.clicked.connect(self.onOkButton)

        self.mainFocusHandler = FocusHandler.InputHandler([
            FocusHandler.SimpleInputFocusProxy(self.ui.withdrawOkButton, ledButtonService),
        ])

        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+c"), self, lambda: self.mainFocusHandler.onLeft())
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+v"), self, lambda: self.mainFocusHandler.onRight())
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+b"), self, lambda: self.mainFocusHandler.onDown())
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+n"), self, lambda: self.mainFocusHandler.onUp())
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+m"), self, lambda: self.mainFocusHandler.onConfirm())

        self.arrowHand = StandardArrowHandler(self, arrowHandler)

        gain = inventoryValues[0]
        prizes = inventoryValues[1]
        moneyTotal = inventoryValues[2]
        moneyFromLastWithdraw = inventoryValues[3]

        inkeeperPerc = AppSettings().actualInkeeperPercentile()

        s = "DEVICE: " + AppSettings.actualDeviceName() + "\n"
        s = s + "OWNER: " + AppSettings.actualOwner() + "\n"
        s = s + datetime.now().strftime("%H:%M:%S         %d/%m/%Y\n")
        s = s + "CURRENCY: " + AppSettings().actualCurrency() + "\n"
        s = s + "SW-version: " + AppSettings.actualAppVersion() + "\n"
        s = s + "Money total: " + "{0:g}".format(moneyTotal) + "\n"
        s = s + "Money from withdraw: " + "{0:g}".format(moneyFromLastWithdraw) + "\n"
        s = s + "Total gain: " + "{0:g}".format(gain) + "\n"
        inkeeperGain = gain * inkeeperPerc /100 if gain > 0 else 0
        ownerGain = gain - inkeeperGain if gain > 0 else 0
        s = s + "Gain owner: " + "{0:g}".format(ownerGain) + "\n"
        s = s + "Gain inkeeper: " + "{0:g}".format(inkeeperGain) + "\n"
        s = s + "Won prizes: " + "\n"

        for key, count in prizes.items():
            name, prize = key.rsplit('-',1)
            s = s + name[0:18] + "/" + "{0:g}".format(float(prize)) + "/" + str(count) + "x\n"

        self.ui.inventoryBrowser.setText(s)

    def onOkButton(self, ledButtonService):
        self.arrowHand.disconnectSignals()
        self.accept()

    def getActualFocusHandler(self):
        return self.mainFocusHandler

    def setFocus(self):
        return self.mainFocusHandler.setFocus()

