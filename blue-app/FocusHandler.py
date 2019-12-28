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

    def onLeft(self):
        self.rotate(-1)
        self.setFocus()

    def onRight(self):
        self.rotate(1)
        self.setFocus()

    def onUp(self):
        self.listOfProxies[0].onUp()

    def onDown(self):
        self.listOfProxies[0].onDown()

    def onConfirm(self):
        self.listOfProxies[0].onConfirm()

    def changeFocusList(self, listOfProxies):
        self.listOfProxies = listOfProxies
        self.setFocus()

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

class TableWidgetFocusProxy(QtCore.QObject):
    def __init__(self, widget):
        super().__init__()
        self.widget = widget

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
        pass

class GenreTableWidgetFocusProxy(TableWidgetFocusProxy):
    def __init__(self, genreWidget, musicController):
        super().__init__(genreWidget)
        self.genreWidget = genreWidget
        self.musicController = musicController

    def onConfirm(self):
        self.musicController.reloadSongsWidget()

class SongTableWidgetFocusProxy(TableWidgetFocusProxy):
    def __init__(self, songWidget, musicController):
        super().__init__(songWidget)
        self.songWidget = songWidget
        self.musicController = musicController

    def onConfirm(self):
        self.musicController.addToPlayQueue()
    
