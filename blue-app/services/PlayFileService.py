from PyQt5 import QtCore

class PlayFileService(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    refreshTimerSignal = QtCore.pyqtSignal(int)

    def __init__(self, parent):
        super().__init__(parent)
        self.process = QtCore.QProcess(self)
        self.refreshTimer = QtCore.QTimer()
        self.refreshTimer.timeout.connect(self.onRefreshTimer)
        self.counter = 0

    def onRefreshTimer(self):
        self.counter = self.counter + 1
        self.refreshTimerSignal.emit(self.counter)

    def playWav(self):
        if self.process.state() == QtCore.QProcess.NotRunning:
            self.process = QtCore.QProcess(self)
            self.process.start("aplay resources/coin-ringtone.wav")

    def emitFinished(self):
        self.refreshTimer.stop()
        self.finished.emit()

    def playMp3(self, mp3info):
        QtCore.QTimer.singleShot(5000, self.emitFinished)
        self.refreshTimer.start(1000)
        #TODO PLAY MP3
