from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

from generated.FortuneWheel import Ui_FortuneWheel
from services.AppSettings import AppSettings
from services.LedButtonService import LedButtonService
from services.PixmapService import PixmapService
from services.PlayFileService import PlayWavFile

from ui import FocusHandler
from collections import deque

class FortuneWheelWindow(QtWidgets.QDialog):
    def __init__(self, parent, winningIndex, prizeName, printingService, ledButtonService, langBasedSettings):
        super(FortuneWheelWindow, self).__init__(parent)
        self.ui = Ui_FortuneWheel()
        self.ui.setupUi(self)

        styleFile = langBasedSettings.getLangBasedQssString()
        styleFile.open(QtCore.QIODevice.ReadOnly)
        data = styleFile.readAll()
        self.setStyleSheet(str(data, encoding="utf-8"))

        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)

        self.winningIndex = winningIndex
        self.realWinName = prizeName
        self.printingService = printingService
        self.ledButtonService = ledButtonService
        self.focusHandler = None

        #QtCore.QTimer.singleShot(1000, lambda: self.onAnimationFinished())
        #self.ui.widget.setFocus()

        self.ledButtonService.setButtonState(LedButtonService.LEFT, False)
        self.ledButtonService.setButtonState(LedButtonService.RIGHT, False)
        self.ledButtonService.setButtonState(LedButtonService.UP, False)
        self.ledButtonService.setButtonState(LedButtonService.DOWN, False)
        self.ledButtonService.setButtonState(LedButtonService.CONFIRM, False)

        self.ui.centerLabel.raise_()

        self.initCounter = 3
        self.initTimer = QtCore.QTimer()
        self.initTimer.timeout.connect(self.onInitTimeout)
        self.initTimer.start(1000)
        self.onInitTimeout()

        self.rotateTimer = QtCore.QTimer()
        self.rotateTimer.timeout.connect(self.onRotateTimer)

        self.maxRotation = 50
        self.maxRotation = self.maxRotation + self.winningIndex
        if self.winningIndex == 0:
           self.maxRotation = self.maxRotation + 10
        self.counter = 0

        PlayWavFile(self).playWav("resources/fortune.wav")

    def rotateImages(self, index):
        indexes = deque(range(0,10))
        indexes.rotate(-1* index)
        self.setPixForLabel(self.ui.leftLabel, PixmapService.pixMaps     [indexes[-2]])
        self.setPixForLabel(self.ui.midLeftLabel, PixmapService.pixMaps  [indexes[-1]])
        self.setPixForLabel(self.ui.centerLabel, PixmapService.pixMaps   [indexes[0 ]])
        self.setPixForLabel(self.ui.midRigthLabel, PixmapService.pixMaps [indexes[1 ]])
        self.setPixForLabel(self.ui.rigthLabel, PixmapService.pixMaps    [indexes[2 ]])

    def onRotateTimer(self):
        self.counter = self.counter + 1
        if (self.counter > 20 and self.counter < 35):
            self.rotateTimer.start(self.rotateTimer.interval() + 5)

        if (self.counter >= 35 and self.counter < 50):
            self.rotateTimer.start(self.rotateTimer.interval() + 10)

        if (self.counter >= 50):
            self.rotateTimer.start(self.rotateTimer.interval() + 25)

        self.rotateImages(self.counter%10)

        if self.counter == self.maxRotation:
            self.rotateTimer.stop()
            QtCore.QTimer.singleShot(1000, self.lastAnimationFinished)

    def setPixForLabel(self, label, pixmap):
        w = label.width()
        h = label.height()
        label.setPixmap(pixmap.scaled(w, h))

    def resetFocus(self):
        if self.focusHandler:
            self.focusHandler.setFocus()

    def openNoWinWindow(self):
        self.ui.stackedWidget.setCurrentIndex(2)

    def openWinWindow(self):
        self.setPixForLabel(self.ui.winLabelPicture, PixmapService.pixMaps[self.winningIndex])
        self.printingService.printTicket(AppSettings.actualDeviceName(), self.winningIndex, self.realWinName)
        self.ui.stackedWidget.setCurrentIndex(3)

    def lastAnimationFinished(self):
        if (self.winningIndex > 0):
            self.openWinWindow()
        else:
            self.openNoWinWindow()

        QtCore.QTimer.singleShot(4000, self.accept)

    def onInitTimeout(self):
        self.initCounter = self.initCounter - 1
        if (self.initCounter == -1):
            self.ui.stackedWidget.setCurrentIndex(1)
            self.rotateTimer.start(100)
            self.initTimer.stop()
        self.ui.timeCounterLabel.setText(str(self.initCounter))

