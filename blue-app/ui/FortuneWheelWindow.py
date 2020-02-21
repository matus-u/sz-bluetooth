from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

from generated.FortuneWheel import Ui_FortuneWheel
from services.AppSettings import AppSettings
from services.LedButtonService import LedButtonService
from services.PixmapService import PixmapService

from ui import FocusHandler
from collections import deque

class FortuneWheelWindow(QtWidgets.QDialog):
    def __init__(self, parent, winningIndex, prizeCount, prizeName, printingService, ledButtonService, arrowHandler):
        super(FortuneWheelWindow, self).__init__(parent)
        self.ui = Ui_FortuneWheel()
        self.ui.setupUi(self)

        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)

        self.arrowHandler = arrowHandler

        self.ui.backButton.clicked.connect(self.accept)
        self.ui.backButton.setEnabled(False)

        self.winningIndex = winningIndex
        self.realWin = (prizeCount > 0)
        self.realWinName = prizeName
        self.printingService = printingService
        self.ledButtonService = ledButtonService
        self.focusHandler = None

        #QtCore.QTimer.singleShot(1000, lambda: self.onAnimationFinished())
        self.ui.widget.setFocus()

        self.ledButtonService.setButtonState(LedButtonService.LEFT, False)
        self.ledButtonService.setButtonState(LedButtonService.RIGHT, False)
        self.ledButtonService.setButtonState(LedButtonService.UP, False)
        self.ledButtonService.setButtonState(LedButtonService.DOWN, False)
        self.ledButtonService.setButtonState(LedButtonService.CONFIRM, False)

        self.ui.centerLabel.raise_()

        self.rotateTimer = QtCore.QTimer()
        self.rotateTimer.timeout.connect(self.onRotateTimer)

        self.maxRotation = 50
        self.maxRotation = self.maxRotation + self.winningIndex
        if self.winningIndex == 0:
           self.maxRotation = self.maxRotation + 10
        self.counter = 0
        self.rotateTimer.start(100)

    def rotateImages(self, index):
        indexes = deque(range(0,10))
        indexes.rotate(-1* index)
        self.setPixForLabel(self.ui.leftLabel, PixmapService.pixMaps     [indexes[-2]])
        self.setPixForLabel(self.ui.midLeftLabel, PixmapService.pixMaps  [indexes[-1 ]])
        self.setPixForLabel(self.ui.centerLabel, PixmapService.pixMaps   [indexes[0 ]])
        self.setPixForLabel(self.ui.midRigthLabel, PixmapService.pixMaps [indexes[1 ]])
        self.setPixForLabel(self.ui.rigthLabel, PixmapService.pixMaps    [indexes[2 ]])

    def onRotateTimer(self):
        self.counter = self.counter + 1
        if self.counter == 30:
            self.rotateTimer.stop()
            self.rotateTimer.start(300)

        if self.counter == 50:
            self.rotateTimer.stop()
            self.rotateTimer.start(500)

        self.rotateImages(self.counter%10)

        if self.counter == self.maxRotation:
            self.rotateTimer.stop()
            self.lastAnimationFinished()

    def setPixForLabel(self, label, pixmap):
        w = label.width()
        h = label.height()
        label.setPixmap(pixmap.scaled(w, h))

    def resetFocus(self):
        if self.focusHandler:
            self.focusHandler.setFocus()

    def lastAnimationFinished(self):
        self.ui.backButton.setEnabled(True)
        if (self.realWin):
            self.ui.wheelLabel.setText(self.tr("Congratulation. Take your ticket! Number: {} Prize: {}").format(self.winningIndex, self.realWinName))
            self.printingService.printTicket(AppSettings.actualDeviceName(), self.winningIndex, self.realWinName)
            self.ui.backButton.setEnabled(True)
            self.focusHandler = FocusHandler.InputHandler([FocusHandler.ButtonFocusProxy(self.ui.backButton, self.ledButtonService, False)])
            self.arrowHandler.confirmClicked.connect(lambda: self.focusHandler.onConfirm())
            QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+m"), self, lambda: self.focusHandler.onConfirm())
        else:
            self.ui.wheelLabel.setText(self.tr("Sorry, no win"))
            QtCore.QTimer.singleShot(2500, self.accept)
