from PyQt5 import QtCore
from PyQt5 import QtMultimedia

class PlayFileService(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    refreshTimerSignal = QtCore.pyqtSignal(int)

    def __init__(self, parent):
        super().__init__(parent)
        self.process = QtCore.QProcess(self)
        self.player = QtMultimedia.QMediaPlayer()
        self.player.stateChanged.connect(self.onPlayerChanged)

    def onPlayerChanged(self, state):
        if state == QtMultimedia.QMediaPlayer.StoppedState:
            self.emitFinished()

    def playWav(self):
        if self.process.state() == QtCore.QProcess.NotRunning:
            self.process = QtCore.QProcess(self)
            self.process.start("aplay resources/coin-ringtone.wav")

    def emitFinished(self):
        self.counter = 0
        self.finished.emit()

    def playMp3(self, mp3info):
        url = QtCore.QUrl.fromLocalFile(mp3info[1])
        content = QtMultimedia.QMediaContent(url)
        self.player.setMedia(content)
        self.player.play()

