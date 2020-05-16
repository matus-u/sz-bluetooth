
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from generated.WithdrawInfo import Ui_WithdrawInfo

from services.LedButtonService import LedButtonService

from ui.ApplicationWindowHelpers import StandardArrowHandler
from ui import FocusHandler

class WithdrawInfoWindow(QtWidgets.QDialog):
    def __init__(self, parent, ledButtonService, arrowHandler, message, title):
        super(WithdrawInfoWindow, self).__init__(parent)

        self.ui = Ui_WithdrawInfo()
        self.ui.setupUi(self)
        self.setWindowTitle(title)
        self.ui.messageLabel.setText(message)
        self.ui.withdrawOkButton.clicked.connect(self.onOkButton)

        self.mainFocusHandler = FocusHandler.InputHandler([
            FocusHandler.ButtonFocusProxy(self.ui.withdrawOkButton, ledButtonService),
        ])

        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+c"), self, lambda: self.mainFocusHandler.onLeft())
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+v"), self, lambda: self.mainFocusHandler.onRight())
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+b"), self, lambda: self.mainFocusHandler.onDown())
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+n"), self, lambda: self.mainFocusHandler.onUp())
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+m"), self, lambda: self.mainFocusHandler.onConfirm())

        self.arrowHand = StandardArrowHandler(self, arrowHandler)

    def onOkButton(self, ledButtonService):
        self.arrowHand.disconnectSignals()
        self.accept()

    def getActualFocusHandler(self):
        return self.mainFocusHandler

    def setFocus(self):
        return self.mainFocusHandler.setFocus()

