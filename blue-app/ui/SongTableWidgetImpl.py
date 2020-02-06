from PyQt5 import QtWidgets
from PyQt5 import QtCore
from generated.SongTableWidget import Ui_SongTableWidget

from ui import Helpers

class SongTableWidgetImpl(QtWidgets.QWidget):

    SELECT_STRING = 'selected'

    def __init__(self, name, duration):
        super(SongTableWidgetImpl, self).__init__()
        self.ui = Ui_SongTableWidget()
        self.ui.setupUi(self)
        self.ui.songNameLabel.setText(name)
        if name == "Bluetooth":
            self.ui.songDurationLabel.setText("--:--")
        else:
            self.ui.songDurationLabel.setText(Helpers.formatDuration(duration))
        self.setProperty(SongTableWidgetImpl.SELECT_STRING, False)

    def select(self):
        if not self.property(SongTableWidgetImpl.SELECT_STRING):
            self.setProperty(SongTableWidgetImpl.SELECT_STRING, True)
            self.setStyleSheet("/* */")

    def deselect(self):
        if self.property(SongTableWidgetImpl.SELECT_STRING):
            self.setProperty(SongTableWidgetImpl.SELECT_STRING, False)
            self.setStyleSheet("/*  */")
