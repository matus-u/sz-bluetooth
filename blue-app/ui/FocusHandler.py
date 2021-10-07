from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

from services.LedButtonService import LedButtonService
from services.GpioCallback import GpioCallback
from services.GpioCallback import GpioCallbackContinous
from services.GpioCallback import GpioTimedCallback
from services.GpioCallback import DoubleButtonHandler

from collections import deque

class ArrowHandler(QtCore.QObject):

    leftClicked = QtCore.pyqtSignal()
    rightClicked = QtCore.pyqtSignal()
    downClicked = QtCore.pyqtSignal(int)
    upClicked = QtCore.pyqtSignal(int)
    confirmClicked = QtCore.pyqtSignal()
    leftAndRightClicked = QtCore.pyqtSignal()
    remoteClicked = QtCore.pyqtSignal()

    def connectGpioContinous(self, gpioService, num, contTime, callback, withFactor):
        gpioCall = GpioCallbackContinous(self, num, contTime, gpioService, withFactor=withFactor)
        gpioCall.callbackGpio.connect(callback)

    def connectGpioOnce(self, gpioService, num, callback):
        gpioCall = GpioCallback(self, num, gpioService)
        gpioCall.callbackGpio.connect(callback)

    def __init__(self, gpioService):
        super().__init__()
        self.connectGpioContinous(gpioService, 29, 300, lambda factor: self.leftClicked.emit(), False)
        self.connectGpioContinous(gpioService, 31, 300, lambda factor: self.rightClicked.emit(), False)
        self.connectGpioContinous(gpioService, 33, 150, lambda factor: self.downClicked.emit(factor), True)
        self.connectGpioContinous(gpioService, 35, 150, lambda factor: self.upClicked.emit(factor), True)
        self.connectGpioOnce(gpioService, 37, lambda: self.confirmClicked.emit())

        gpioBothCall = DoubleButtonHandler(self, gpioService, 29, 31)
        gpioBothCall.bothClick.connect(lambda: self.leftAndRightClicked.emit())

        gpioTimedCallback = GpioTimedCallback(self, 24, 6000, gpioService)
        gpioTimedCallback.callbackGpio.connect(lambda: self.remoteClicked.emit())

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
        rotateAgain = rotateAgain or self.listOfProxies[0].notInterestedInFocus()
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

    def onUp(self, factor=1):
        self.findFocusedWidget().onUp(factor)

    def onDown(self, factor=1):
        self.findFocusedWidget().onDown(factor)

    def onConfirm(self):
        proxy = self.findFocusedWidget().onConfirm()

    def changeFocusList(self, listOfProxies):
        self.listOfProxies = listOfProxies
        self.setFocus()

class FocusNullObject:
    def __init__(self, widget=None):
        self.widget = widget

    def setFocus(self):
        pass

    def onUp(self, factor):
        pass

    def onDown(self, factor):
        pass

    def onLeft(self):
        pass

    def onRight(self):
        pass

    def onConfirm(self):
        pass

    def getManangedWidget(self):
        return self.widget

    def notInterestedInFocus(self):
        return False

class SimpleInputFocusProxy:
    def __init__(self, inputWidget, ledButtonService, arrowsEnabled=True):
        self.inputWidget = inputWidget
        self.ledButtonService = ledButtonService
        self.arrowsEnabled = arrowsEnabled

    def setFocus(self):
        self.inputWidget.setFocus()
        self.ledButtonService.setButtonState(LedButtonService.LEFT, self.arrowsEnabled)
        self.ledButtonService.setButtonState(LedButtonService.RIGHT, self.arrowsEnabled)
        self.ledButtonService.setButtonState(LedButtonService.UP, False)
        self.ledButtonService.setButtonState(LedButtonService.DOWN, False)
        self.ledButtonService.setButtonState(LedButtonService.CONFIRM, True)

    def onUp(self, factor):
        pass

    def onDown(self, factor):
        pass

    def onLeft(self):
        pass

    def onRight(self):
        pass

    def onConfirm(self):
        self.inputWidget.animateClick()

    def getManangedWidget(self):
        return self.inputWidget

    def notInterestedInFocus(self):
        return False

class TableWidgetFocusProxy(QtCore.QObject):
    def __init__(self, widget, confirmHandler, ledButtonService, musicControl = None, notInterestedInFocusFunc = None):
        super().__init__()
        self.widget = widget
        self.confirmHandler = confirmHandler
        self.ledButtonService = ledButtonService

        self.musicControl = musicControl
        self.notInterestedInFocusFunc = notInterestedInFocusFunc

    def onLeft(self):
        if self.musicControl:
            self.musicControl.previousGenre()

    def onRight(self):
        if self.musicControl:
            self.musicControl.nextGenre()

    def getManangedWidget(self):
        return self.widget

    def setFocus(self):
        self.widget.setFocus()
        self.ledButtonService.setButtonState(LedButtonService.LEFT, True)
        self.ledButtonService.setButtonState(LedButtonService.RIGHT, True)
        self.ledButtonService.setButtonState(LedButtonService.UP, True)
        self.ledButtonService.setButtonState(LedButtonService.DOWN, True)
        self.ledButtonService.setButtonState(LedButtonService.CONFIRM, True)

    def getUnderlyingWidgetRowCount(self):
        return self.widget.rowCount()

    def onUp(self, factor):
        if self.getUnderlyingWidgetRowCount() > 0:
            if len(self.widget.selectionModel().selectedRows()) > 0:
                row = self.widget.selectionModel().selectedRows()[0].row()
                if (self.getUnderlyingWidgetRowCount() - factor) > row:
                    self.widget.selectRow(row + factor)
                else:
                    self.widget.selectRow(0)
            else:
                self.widget.selectRow(self.getUnderlyingWidgetRowCount() - 1)

    def onDown(self, factor):
        if self.getUnderlyingWidgetRowCount() > 0:
            if len(self.widget.selectionModel().selectedRows()) > 0:
                row = self.widget.selectionModel().selectedRows()[0].row()
                if row - factor > 0:
                    self.widget.selectRow(row - factor)
                else:
                    self.widget.selectRow(self.getUnderlyingWidgetRowCount() - 1)
            else:
                self.widget.selectRow(0)

    def onConfirm(self):
        if self.confirmHandler:
            self.confirmHandler()

    def notInterestedInFocus(self):
        if self.notInterestedInFocusFunc is not None:
            return self.notInterestedInFocusFunc()
        return False

class MusicWidgetFocusProxy(TableWidgetFocusProxy):
    def __init__(self, widget, confirmHandler, ledButtonService, musicControl, notInterestedInFocusFunc=None):
        super().__init__(widget, confirmHandler, ledButtonService, notInterestedInFocusFunc=notInterestedInFocusFunc)
        self.musicControl = musicControl

    def onLeft(self):
        self.musicControl.previousGenre()

    def onRight(self):
        self.musicControl.nextGenre()

    def getUnderlyingWidgetRowCount(self):
        return self.musicControl.rowCount()

class LanguageLabelFocusProxy(SimpleInputFocusProxy):
    def __init__(self, widget, ledButtonService, tempLanguageChanger):
        super().__init__(widget, ledButtonService)
        self.tempLanguageChanger = tempLanguageChanger

    def onLeft(self):
        self.tempLanguageChanger.moveLanguageLeft()

    def onRight(self):
        self.tempLanguageChanger.moveLanguageRight()

    def onConfirm(self):
        self.tempLanguageChanger.confirmLanguageChange()

class TextBrowserFocusProxy(SimpleInputFocusProxy):
    def __init__(self, textBrowser, ledButtonService, musicControl, confirmHandler):
        super().__init__(textBrowser, ledButtonService)

        self.musicControl = musicControl
        self.confirmHandler = confirmHandler

    def onLeft(self):
        self.musicControl.previousGenre()

    def onRight(self):
        self.musicControl.nextGenre()

    def onConfirm(self):
        self.confirmHandler()
