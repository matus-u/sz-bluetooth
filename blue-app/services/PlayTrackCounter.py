from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

class PlayTrackCounter(QtCore.QObject):

    SettingsPath = "../blue-app-configs/track-counter.conf"
    SettingsFormat = QtCore.QSettings.NativeFormat

    Counts = "Counts"

    countUpdated = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.musicCounters = {}

        self.settings = QtCore.QSettings(PlayTrackCounter.SettingsPath, PlayTrackCounter.SettingsFormat)
        self.musicCounters = self.settings.value(PlayTrackCounter.Counts, {})

    def addToCounter(self, path):
        count = self.musicCounters.get(name, 0)
        count = count + 1
        self.musicCounters[name] = c
        self.settings.setValue(PlayTrackCounter.Counts, self.musicCounters)
        self.countUpdated.emit(path)

