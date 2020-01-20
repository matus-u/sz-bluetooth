from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

from services.LedButtonService import LedButtonService

from collections import deque 

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

    def onRight(self):
        self.rotate(1)
        self.setFocus()

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

    def onConfirm(self):
        pass

class ButtonFocusProxy:
    def __init__(self, button, ledButtonService):
        self.button = button
        self.ledButtonService = ledButtonService

    def setFocus(self):
        self.button.setFocus()
        self.ledButtonService.setButtonState(LedButtonService.LEFT, True)
        self.ledButtonService.setButtonState(LedButtonService.RIGHT, True)
        self.ledButtonService.setButtonState(LedButtonService.UP, False)
        self.ledButtonService.setButtonState(LedButtonService.DOWN, False)
        self.ledButtonService.setButtonState(LedButtonService.CONFIRM, True)

    def onUp(self):
        pass

    def onDown(self):
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
