from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from generated.TestHw import Ui_TestHw

from services.PlayFileService import PlayWavFile
from services.LedButtonService import LedButtonService

class TestHwWindow(QtWidgets.QDialog):
    def __init__(self, parent, printerService, ledButtonService):
        super(TestHwWindow, self).__init__(parent)

        self.ui = Ui_TestHw()
        self.ui.setupUi(self)

        self.ui.testPrinterButton.clicked.connect(lambda: printerService.printTestTicket())
        self.ui.testSoundButton.clicked.connect(self.onTestSoundButton)
        self.ui.testLedButton.clicked.connect(lambda: self.onTestLedButton(ledButtonService))
        self.ui.closeButton.clicked.connect(self.accept)

        self.disableLedButtonStates(ledButtonService)
        self.ledButtonIndex = 0
        self.ledButtonIndexArray = [ LedButtonService.DOWN, LedButtonService.UP, LedButtonService.LEFT, LedButtonService.RIGHT, LedButtonService.CONFIRM ]
        self.ledButtonTimer = QtCore.QTimer(self)
        self.ledButtonTimer.timeout.connect(lambda: self.onLedButtonTimer(ledButtonService))

    def onTestLedButton(self, ledButtonService):
        self.ui.testLedButton.setEnabled(False)
        self.onLedButtonTimer(ledButtonService)
        self.ledButtonTimer.start(2000)
        QtCore.QTimer.singleShot(10000, lambda: self.onLedButtonTimerFinished(ledButtonService))

    def disableLedButtonStates(self, ledButtonService):
        ledButtonService.setButtonState(LedButtonService.DOWN, False)
        ledButtonService.setButtonState(LedButtonService.UP, False)
        ledButtonService.setButtonState(LedButtonService.LEFT, False)
        ledButtonService.setButtonState(LedButtonService.RIGHT, False)
        ledButtonService.setButtonState(LedButtonService.CONFIRM, False)

    def onLedButtonTimer(self, ledButtonService):
        self.disableLedButtonStates(ledButtonService)
        ledButtonService.setButtonState(self.ledButtonIndexArray[self.ledButtonIndex], True)
        self.ledButtonIndex = (self.ledButtonIndex + 1)%5

    def onLedButtonTimerFinished(self, ledButtonService):
        self.ledButtonTimer.stop()
        self.disableLedButtonStates(ledButtonService)
        self.ledButtonIndex = 0
        self.ui.testLedButton.setEnabled(True)

    def onTestSoundButton(self):
        PlayWavFile(self).playWav("resources/fortune.wav")

