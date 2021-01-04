from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

from services import PathSettings
import os

class PlayTrackCounter(QtCore.QObject):

    SettingsPath = PathSettings.AppBasePath() + "../blue-app-configs/track-counter.conf"
    SettingsFormat = QtCore.QSettings.NativeFormat

    Counts = "Counts"

    countUpdated = QtCore.pyqtSignal(str, int)

    def __init__(self):
        super().__init__()
        self.musicCounters = {}

        self.settings = QtCore.QSettings(PlayTrackCounter.SettingsPath, PlayTrackCounter.SettingsFormat)
        self.musicCounters = self.settings.value(PlayTrackCounter.Counts, {})
        self.musicCounters = {k: v for k, v in self.musicCounters.items() if os.path.isfile(k)}
        self.topTracks = self.calculateTopTrackNames()

    def addToCounter(self, path):
        count = self.musicCounters.get(path, 0)
        count = count + 1
        self.musicCounters[path] = count
        self.settings.setValue(PlayTrackCounter.Counts, self.musicCounters)
        self.countUpdated.emit(path, count)
        self.topTracks = self.calculateTopTrackNames()

    def getCount(self, path):
        return self.musicCounters.get(path, 0)

    def calculateTopTrackNames(self):
        l = list(self.musicCounters.items())
        l.sort(key=lambda x:(-1*x[1], x[0]))
        return l[:30]

    def topTrackNames(self):
        return self.topTracks

