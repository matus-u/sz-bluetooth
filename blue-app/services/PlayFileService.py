from PyQt5 import QtCore

class PlayFileService(QtCore.QObject):
    def __init__(self, parent):
        super().__init__(parent)
        self.process = QtCore.QProcess(self)

    def play(self):
        if self.process.state() == QtCore.QProcess.NotRunning:
            self.process = QtCore.QProcess(self)
            self.process.start("aplay resources/coin-ringtone.wav")
