from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from generated.WithdrawAsk import Ui_WithdrawAsk

from services.LedButtonService import LedButtonService

from ui.ApplicationWindowHelpers import StandardArrowHandler
from ui import FocusHandler

class WithdrawAskWindow(QtWidgets.QDialog):
    def __init__(self, parent, ledButtonService, arrowHandler, message, title):
        super(WithdrawAskWindow, self).__init__(parent)

        self.ui = Ui_WithdrawAsk()
        self.ui.setupUi(self)
        self.setWindowTitle(title)
        self.ui.messageLabel.setText(message)
        self.ui.yesButton.clicked.connect(self.onYesButton)
        self.ui.noButton.clicked.connect(self.onNoButton)

        self.mainFocusHandler = FocusHandler.InputHandler([
            FocusHandler.SimpleInputFocusProxy(self.ui.noButton, ledButtonService),
            FocusHandler.SimpleInputFocusProxy(self.ui.yesButton, ledButtonService)
        ])

        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+c"), self, lambda: self.mainFocusHandler.onLeft())
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+v"), self, lambda: self.mainFocusHandler.onRight())
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+b"), self, lambda: self.mainFocusHandler.onDown())
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+n"), self, lambda: self.mainFocusHandler.onUp())
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+m"), self, lambda: self.mainFocusHandler.onConfirm())

        self.arrowHand = StandardArrowHandler(self, arrowHandler)

    def onYesButton(self, ledButtonService):
        self.arrowHand.disconnectSignals()
        self.accept()

    def onNoButton(self, ledButtonService):
        self.arrowHand.disconnectSignals()
        self.reject()

    def getActualFocusHandler(self):
        return self.mainFocusHandler

    def setFocus(self):
        return self.mainFocusHandler.setFocus()

