from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from generated.TestHw import Ui_TestHw

from services.PlayFileService import PlayWavFile
from services.LedButtonService import LedButtonService

class TestHwWindow(QtWidgets.QDialog):
    def __init__(self, parent, printerService, ledButtonService, coinProtocolService, volumeService, arrowHandler, wheelService, errorHwHandler):
        super(TestHwWindow, self).__init__(parent)

        self.ui = Ui_TestHw()
        self.ui.setupUi(self)

        self.ui.testPrinterButton.clicked.connect(lambda: self.onTestPrinterButton(printerService, errorHwHandler))
        self.ui.testSoundButton.clicked.connect(self.onTestSoundButton)
        self.ui.testLedButton.clicked.connect(lambda: self.onTestLedButton(ledButtonService))
        self.ui.closeButton.clicked.connect(self.accept)
        self.ui.ventilatorButton.clicked.connect(self.enableVentilator)

        self.ledButtonIndex = 0
        self.ledButtonIndexArray = [ LedButtonService.DOWN, LedButtonService.UP, LedButtonService.LEFT, LedButtonService.RIGHT, LedButtonService.CONFIRM ]
        self.ledButtonTimer = QtCore.QTimer(self)
        self.ledButtonTimer.timeout.connect(lambda: self.onLedButtonTimer(ledButtonService))

        coinProtocolService.actualStatus.connect(self.onCoinProtocolService)

        volumeService.signalVolumeUp.connect(lambda: self.updateRemoveControllerTableWidget(0), QtCore.Qt.QueuedConnection)
        volumeService.signalVolumeDown.connect(lambda: self.updateRemoveControllerTableWidget(1), QtCore.Qt.QueuedConnection)
        volumeService.signalMute.connect(lambda: self.updateRemoveControllerTableWidget(2), QtCore.Qt.QueuedConnection)

        arrowHandler.rightClicked.connect(lambda: self.updateButtonTestTableWidget(0))
        arrowHandler.leftClicked.connect(lambda: self.updateButtonTestTableWidget(1))
        arrowHandler.upClicked.connect(lambda: self.updateButtonTestTableWidget(3))
        arrowHandler.downClicked.connect(lambda: self.updateButtonTestTableWidget(2))
        arrowHandler.confirmClicked.connect(lambda: self.updateButtonTestTableWidget(4))

        self.disableLedButtonStates(ledButtonService)

        self.ui.testSoundButton.setFocus()
        self.ui.fortuneWheelTest.clicked.connect(lambda: self.ui.fortuneWheelTestOutput.setText(wheelService.testWinn()))

    def onTestPrinterButton(self, printerService, errorHwHandler):
        if errorHwHandler.isPrinterErrorSet():
            QtWidgets.QMessageBox.warning(self, self.tr("Printer errors:"), "\n".join(errorHwHandler.getPrinterErrorDescs()))
            return
        printerService.printTestTicket()
    
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

    def onCoinProtocolService(self, channel, count):
        self.ui.coinMachineTableWidget.setItem(channel,1, QtWidgets.QTableWidgetItem(str(int(self.ui.coinMachineTableWidget.item(channel, 1).text()) + count)))

    def updateRemoveControllerTableWidget(self, index):
        self.ui.remoteControlerTableWidget.setItem(index,1 ,QtWidgets.QTableWidgetItem(str(int(self.ui.remoteControlerTableWidget.item(index, 1).text()) + 1)))

    def updateButtonTestTableWidget(self, index):
        self.ui.buttonTestTableWidget.setItem(index,1 ,QtWidgets.QTableWidgetItem(str(int(self.ui.buttonTestTableWidget.item(index, 1).text()) + 1)))

    def enableVentilator(self):
        QtCore.QProcess.execute("scripts/setup-ventilator.sh", ["1"])
