from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

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
    def __init__(self, button):
        self.button = button

    def setFocus(self):
        self.button.setFocus()

    def onUp(self):
        pass

    def onDown(self):
        pass

    def onConfirm(self):
        self.button.animateClick()

    def getManangedWidget(self):
        return self.button

class TableWidgetFocusProxy(QtCore.QObject):
    def __init__(self, widget, confirmHandler):
        super().__init__()
        self.widget = widget
        self.confirmHandler = confirmHandler

    def getManangedWidget(self):
        return self.widget

    def setFocus(self):
        self.widget.setFocus()

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
