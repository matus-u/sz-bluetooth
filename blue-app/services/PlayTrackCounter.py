from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

class PlayTrackCounter(QtCore.QObject):

    SettingsPath = "../blue-app-configs/track-counter.conf"
    SettingsFormat = QtCore.QSettings.NativeFormat

    Counts = "Counts"

    countUpdated = QtCore.pyqtSignal(str, int)

    def __init__(self):
        super().__init__()
        self.musicCounters = {}

        self.settings = QtCore.QSettings(PlayTrackCounter.SettingsPath, PlayTrackCounter.SettingsFormat)
        self.musicCounters = self.settings.value(PlayTrackCounter.Counts, {})

    def addToCounter(self, path):
        count = self.musicCounters.get(path, 0)
        count = count + 1
        self.musicCounters[path] = count
        self.settings.setValue(PlayTrackCounter.Counts, self.musicCounters)
        self.countUpdated.emit(path, count)

    def getCount(self, path):
        return self.musicCounters.get(path, 0)

    def topTrackNames(self):
        l = list(self.musicCounters.items())
        l.sort(key=lambda x:(-1*x[1], x[0]))
        return l[:30]
