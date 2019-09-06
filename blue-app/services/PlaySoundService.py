from PyQt5 import QtCore

class PlaySoundService():
    def __init__(self):
        self.process = QtCore.QProcess()

    def play(self):
        if self.process.state() == QtCore.QProcess.NotRunning:
            self.process = QtCore.QProcess()
            self.process.start("aplay resources/coin-ringtone.wav")
