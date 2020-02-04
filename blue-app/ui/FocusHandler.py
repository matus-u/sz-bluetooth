from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

from services.LedButtonService import LedButtonService
from services.GpioCallback import GpioCallback

from collections import deque

class ArrowHandler(QtCore.QObject):

    leftClicked = QtCore.pyqtSignal()
    rightClicked = QtCore.pyqtSignal()
    downClicked = QtCore.pyqtSignal()
    upClicked = QtCore.pyqtSignal()
    confirmClicked = QtCore.pyqtSignal()

    def connectGpio(self, gpioService, num, callback):
        gpioCall = GpioCallback(self)
        gpioCall.callbackGpio.connect(callback, QtCore.Qt.QueuedConnection)
        gpioService.registerCallback(gpioService.FALLING, num, gpioCall.onLowLevelCallback)

    def __init__(self, gpioService):
        super().__init__()
        self.connectGpio(gpioService, 29, lambda: self.leftClicked.emit())
        self.connectGpio(gpioService, 31, lambda: self.rightClicked.emit())
        self.connectGpio(gpioService, 33, lambda: self.downClicked.emit())
        self.connectGpio(gpioService, 35, lambda: self.upClicked.emit())
        self.connectGpio(gpioService, 37, lambda: self.confirmClicked.emit())

class InputHandler(QtCore.QObject):
    def __init__(self, listOfProxies):
        super().__init__()
        self.listOfProxies = listOfProxies
        self.setFocus()

    def setFocus(self):
        self.listOfProxies[0].setFocus()

    def rotate(self, value):
        l = deque(self.listOfProxies)
        l.rotate(value)
        self.listOfProxies = list(l)
        rotateAgain = (not self.listOfProxies[0].getManangedWidget().isEnabled()) or (not self.listOfProxies[0].getManangedWidget().isVisible())
        if rotateAgain:
            self.rotate(value)

    def onLeft(self):
        self.rotate(-1)
        self.setFocus()
        self.findFocusedWidget().onLeft()

    def onRight(self):
        self.rotate(1)
        self.setFocus()
        self.findFocusedWidget().onRight()

    def findFocusedWidget(self):
        focusedWidget = QtWidgets.QApplication.focusWidget()
        for w in self.listOfProxies:
            if w.getManangedWidget() == focusedWidget:
                return w
        return FocusNullObject()

    def onUp(self):
        self.findFocusedWidget().onUp()

    def onDown(self):
        self.findFocusedWidget().onDown()

    def onConfirm(self):
        proxy = self.findFocusedWidget().onConfirm()

    def changeFocusList(self, listOfProxies):
        self.listOfProxies = listOfProxies
        self.setFocus()

class FocusNullObject:
    def setFocus(self):
        pass

    def onUp(self):
        pass

    def onDown(self):
        pass

    def onLeft(self):
        pass

    def onRight(self):
        pass

    def onConfirm(self):
        pass

class ButtonFocusProxy:
    def __init__(self, button, ledButtonService, arrowsEnabled=True):
        self.button = button
        self.ledButtonService = ledButtonService
        self.arrowsEnabled = arrowsEnabled

    def setFocus(self):
        self.button.setFocus()
        self.ledButtonService.setButtonState(LedButtonService.LEFT, self.arrowsEnabled)
        self.ledButtonService.setButtonState(LedButtonService.RIGHT, self.arrowsEnabled)
        self.ledButtonService.setButtonState(LedButtonService.UP, False)
        self.ledButtonService.setButtonState(LedButtonService.DOWN, False)
        self.ledButtonService.setButtonState(LedButtonService.CONFIRM, True)

    def onUp(self):
        pass

    def onDown(self):
        pass

    def onLeft(self):
        pass

    def onRight(self):
        pass

    def onConfirm(self):
        self.button.animateClick()

    def getManangedWidget(self):
        return self.button

class TableWidgetFocusProxy(QtCore.QObject):
    def __init__(self, widget, confirmHandler, ledButtonService):
        super().__init__()
        self.widget = widget
        self.confirmHandler = confirmHandler
        self.ledButtonService = ledButtonService

    def getManangedWidget(self):
        return self.widget

    def setFocus(self):
        self.widget.setFocus()
        self.ledButtonService.setButtonState(LedButtonService.LEFT, True)
        self.ledButtonService.setButtonState(LedButtonService.RIGHT, True)
        self.ledButtonService.setButtonState(LedButtonService.UP, True)
        self.ledButtonService.setButtonState(LedButtonService.DOWN, True)
        self.ledButtonService.setButtonState(LedButtonService.CONFIRM, True)

    def onUp(self):
        if self.widget.rowCount() > 0:
            if len(self.widget.selectionModel().selectedRows()) > 0:
                row = self.widget.selectionModel().selectedRows()[0].row()
                if (self.widget.rowCount() - 1) > row:
                    self.widget.selectRow(row + 1)
                else:
                    self.widget.selectRow(0)
            else:
                self.widget.selectRow(self.widget.rowCount() - 1)

    def onDown(self):
        if self.widget.rowCount() > 0:
            if len(self.widget.selectionModel().selectedRows()) > 0:
                row = self.widget.selectionModel().selectedRows()[0].row()
                if row > 0:
                    self.widget.selectRow(row - 1)
                else:
                    self.widget.selectRow(self.widget.rowCount() - 1)
            else:
                self.widget.selectRow(0)

    def onConfirm(self):
        if self.confirmHandler:
            self.confirmHandler()

    def onLeft(self):
        pass

    def onRight(self):
        pass

class MusicWidgetFocusProxy(TableWidgetFocusProxy):
    def __init__(self, widget, confirmHandler, ledButtonService, musicControl):
        super().__init__(widget, confirmHandler, ledButtonService)
        self.musicControl = musicControl

    def onLeft(self):
        self.musicControl.previousGenre()

    def onRight(self):
        self.musicControl.nextGenre()


