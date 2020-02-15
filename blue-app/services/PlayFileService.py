from PyQt5 import QtCore
from PyQt5 import QtMultimedia

import os

from services.LoggingService import LoggingService

class PlayFileService(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    refreshTimerSignal = QtCore.pyqtSignal(int)

    def __init__(self, parent):
        super().__init__(parent)
        self.process = QtCore.QProcess(self)
        self.player = QtMultimedia.QMediaPlayer()
        self.player.stateChanged.connect(self.onPlayerChanged)
        self.player.error.connect(self.onError)

    def onPlayerChanged(self, state):
        if state == QtMultimedia.QMediaPlayer.StoppedState:
            self.emitFinished()

    def onError(self, error):
        LoggingService.getLogger().info("Mp3 Error:".format(self.player.errorString()))
        if not (os.getenv('RUN_FROM_DOCKER', False) == False):
            return

        self.emitFinished()

    def playWav(self):
        if self.process.state() == QtCore.QProcess.NotRunning:
            self.process = QtCore.QProcess(self)
            self.process.start("aplay resources/coin-ringtone.wav")

    def emitFinished(self):
        self.finished.emit()

    def playMp3(self, path):
        url = QtCore.QUrl.fromLocalFile(path)
        content = QtMultimedia.QMediaContent(url)
        LoggingService.getLogger().info("Mp3 play:".format(path))
        self.player.setMedia(content)
        self.player.play()

        if not (os.getenv('RUN_FROM_DOCKER', False) == False):
            QtCore.QTimer.singleShot(10000, lambda: self.emitFinished())

