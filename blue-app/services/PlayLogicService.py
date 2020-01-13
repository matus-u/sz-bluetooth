from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

from services.PlayFileService import PlayFileService

class PlayLogicService(QtCore.QObject):

    playingStarted = QtCore.pyqtSignal()
    playingFailed = QtCore.pyqtSignal()
    refreshTimerSignal = QtCore.pyqtSignal(int)
    playingStopped = QtCore.pyqtSignal()

    def __init__(self, bluetoothService, playQueue):
        super().__init__()
        self.playQueue = playQueue
        self.bluetoothService = bluetoothService
        self.state = "IDLE"

        self.bluetoothService.disconnectedEndSignal.connect(self.onPlayingFinished)
        self.bluetoothService.connectedSignal.connect(self.onConnectedSignal)
        self.mp3info = []

        self.playService = PlayFileService(self)
        self.playService.finished.connect(self.onPlayingFinished)

        self.refreshTimer = QtCore.QTimer()
        self.refreshTimer.timeout.connect(self.onRefreshTimer)
        self.counter = 0

    def onRefreshTimer(self):
        self.counter = self.counter + 1
        self.refreshTimerSignal.emit(self.counter)

    def playFromBluetooth(self, macAddr, duration):
        if self.state == "IDLE":
            self.state = "BLUETOOTH"
            self.bluetoothService.connect(macAddr, duration)
        else:
            print("ERROR")

    def startPlaying(self, mp3info):
        self.state = "PLAYING"
        self.mp3info = mp3info
        self.playService.playMp3(mp3info)
        self.playingStarted.emit()
        self.counter = 0
        self.refreshTimer.start(1000)
            
    def playFromLocal(self, mp3info):
        if self.state == "IDLE":
            self.startPlaying(mp3info)
        else:
            self.playQueue.addToPlayQueue(mp3info)

    def onConnectedSignal(self, exitCode):
        if exitCode == 1:
            self.playingFailed.emit()
            self.state = "IDLE"
        else:
            self.playingStarted.emit()
            self.counter = 0
            self.refreshTimer.start(1000)

    def onPlayingFinished(self):
        if (self.playQueue.isEmpty()):
            self.playingStopped.emit()
            self.state = "IDLE"
            self.counter = 0
            self.refreshTimer.stop()
        else:
            self.startPlaying(self.playQueue.popFromPlayQueue())

    def isPlaying(self):
        return self.state != "IDLE"

    def isPlayingFromBluetooth(self):
        return self.state == "BLUETOOTH"

    def getActualPlayingMp3(self):
        return self.mp3info

