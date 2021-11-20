from PyQt5 import QtCore
from PyQt5 import QtMultimedia

import os

from services.LoggingService import LoggingService

class PlayWavFile(QtCore.QObject):

    def __init__(self, parent):
        super().__init__(parent)
        self.process = QtCore.QProcess(self)
        self.process.finished.connect(self.onFinished)

    def playWav(self, path):
        self.process.start("aplay -Dsoftvolsound " + path)

    def onFinished(self,a,b):
        self.deleteLater()

class PlayFileService(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    refreshTimerSignal = QtCore.pyqtSignal(int)

    def __init__(self, parent, videoWidget):
        super().__init__(parent)
        self.player = QtMultimedia.QMediaPlayer()
        self.player.stateChanged.connect(self.onPlayerChanged)
        self.player.error.connect(self.onError)
        self.videoWidget = videoWidget
        self.player.setVideoOutput(videoWidget)

    def onPlayerChanged(self, state):
        if state == QtMultimedia.QMediaPlayer.StoppedState:
            self.finished.emit()

    def onError(self, error):
        LoggingService.getLogger().info("Mp3 Error:".format(self.player.errorString()))
        if not (os.getenv('RUN_FROM_DOCKER', False) == False):
            return

        LoggingService.getLogger().info("Mp3 finished.")
        self.videoWidget.hide()
        self.finished.emit()

    def play(self, path, withVideo):
        url = QtCore.QUrl.fromLocalFile(path)
        content = QtMultimedia.QMediaContent(url)
        LoggingService.getLogger().info("Mp3 play:".format(path))
        self.player.setMedia(content)
        self.player.play()

        if not (os.getenv('RUN_FROM_DOCKER', False) == False):
            QtCore.QTimer.singleShot(10000, lambda: self.finished.emit())

