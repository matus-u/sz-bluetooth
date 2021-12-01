from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtCore
from generated.SongTableWidget import Ui_SongTableWidget

from model.PlayQueue import Mp3PlayQueueObject, BluetoothPlayQueueObject

from ui import Helpers

class SongTableWidgetImpl(QtWidgets.QWidget):

    SELECT_STRING = 'selected'

    def __init__(self, name, playQueueObject, durationVisible, countVisible, playTrackCounter):
        super(SongTableWidgetImpl, self).__init__()
        self.ui = Ui_SongTableWidget()
        self.ui.setupUi(self)
        self.ui.songNameLabel.setText(name)
        self.duration = playQueueObject.duration()
        self.setDurationVisible(durationVisible)
        self.setProperty(SongTableWidgetImpl.SELECT_STRING, False)
        self.playQueueObject = playQueueObject
        self.playTrackCounter = playTrackCounter
        self.originalText = ""
        self.justifiedText = ""
        self.movingTextTimer = QtCore.QTimer(self)
        self.movingTextTimer.timeout.connect(self.onMovingTimer)

        if (countVisible):
            self.ui.playCountLabel.setText(self.formatCountValue(playTrackCounter.getCount(playQueueObject.path())))
            playTrackCounter.countUpdated.connect(self.onPlayCountChange)

    def formatCountValue(self, value):
        return '{0:04d}'.format(value)

    def onPlayCountChange(self, itemPath, value):
        if itemPath == self.playQueueObject.path():
            self.ui.playCountLabel.setText(self.formatCountValue(value))

    def setDurationVisible(self, visible):
        if visible:
            self.ui.songDurationLabel.setText(Helpers.formatDuration(self.duration, self.ui.songNameLabel.text()))
        else:
            self.ui.songDurationLabel.setText("")

    def updateFromPlayQueueObject(self, playQueueObject, durationVisible):
        self.playQueueObject = playQueueObject
        self.ui.songNameLabel.setText(self.playQueueObject.name())
        self.duration = playQueueObject.duration()
        self.setDurationVisible(durationVisible)
        self.originalText = self.playQueueObject.name()
        self._resetJustifiedText()

        if not isinstance(playQueueObject, BluetoothPlayQueueObject):
            self.ui.playCountLabel.setText(self.formatCountValue(self.playTrackCounter.getCount(playQueueObject.path())))
        else:
            self.ui.playCountLabel.setText("")

    @classmethod
    def fromPlayQueueObject(cls, playQueueObject, useStartTime, durationVisible, countVisible, playTrackCounter=None):
        if isinstance(playQueueObject, BluetoothPlayQueueObject):
            nameToShow = playQueueObject.name()
            if useStartTime:
                nameToShow = Helpers.formatNameWithStartTime(playQueueObject.name(), playQueueObject.startTime())
            return cls(nameToShow, playQueueObject, durationVisible, False, None)

        if isinstance(playQueueObject, Mp3PlayQueueObject):
            return cls(playQueueObject.name(), playQueueObject, durationVisible, countVisible, playTrackCounter)


    def select(self):
        if not self.property(SongTableWidgetImpl.SELECT_STRING):
            self.setProperty(SongTableWidgetImpl.SELECT_STRING, True)
            self.setStyleSheet("/* */")
        self.ui.songNameLabel.setText(self.originalText)
        if self._resetJustifiedText():
            self.movingTextTimer.start(150)
        else:
            self.movingTextTimer.stop()


    def deselect(self):
        if self.property(SongTableWidgetImpl.SELECT_STRING):
            self.setProperty(SongTableWidgetImpl.SELECT_STRING, False)
            self.setStyleSheet("/*  */")

        self.ui.songNameLabel.setText(self.originalText)
        self.movingTextTimer.stop()

    def onMovingTimer(self):
        self.justifiedText = self.justifiedText[1:] + self.justifiedText[0]
        self.ui.songNameLabel.setText(self.justifiedText)

    def _resetJustifiedText(self):
        if len(self.originalText) > 36:
            self.justifiedText = self.originalText + "     "
            return True

        self.justifiedText = "{:36}".format(self.originalText)
        return False
