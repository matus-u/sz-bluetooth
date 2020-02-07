from PyQt5 import QtWidgets
from PyQt5 import QtCore
from generated.SongTableWidget import Ui_SongTableWidget

from model.PlayQueue import Mp3PlayQueueObject, BluetoothPlayQueueObject

from ui import Helpers

class SongTableWidgetImpl(QtWidgets.QWidget):

    SELECT_STRING = 'selected'

    def __init__(self, name, duration):
        super(SongTableWidgetImpl, self).__init__()
        self.ui = Ui_SongTableWidget()
        self.ui.setupUi(self)
        self.ui.songNameLabel.setText(name)
        self.ui.songDurationLabel.setText(Helpers.formatDuration(duration, name))
        self.setProperty(SongTableWidgetImpl.SELECT_STRING, False)

    @classmethod
    def fromPlayQueueObject(cls, playQueueObject):
        if isinstance(playQueueObject, BluetoothPlayQueueObject):
            return cls(Helpers.formatNameWithStartTime(playQueueObject.name(), playQueueObject.startTime()), playQueueObject.duration())

        if isinstance(playQueueObject, Mp3PlayQueueObject):
            return cls(playQueueObject.name(), playQueueObject.duration())


    def select(self):
        if not self.property(SongTableWidgetImpl.SELECT_STRING):
            self.setProperty(SongTableWidgetImpl.SELECT_STRING, True)
            self.setStyleSheet("/* */")

    def deselect(self):
        if self.property(SongTableWidgetImpl.SELECT_STRING):
            self.setProperty(SongTableWidgetImpl.SELECT_STRING, False)
            self.setStyleSheet("/*  */")
