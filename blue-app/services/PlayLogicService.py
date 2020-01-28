from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

from services.PlayFileService import PlayFileService
from model.PlayQueue import Mp3PlayQueueObject, BluetoothPlayQueueObject

class PlayLogicService(QtCore.QObject):

    playingStarted = QtCore.pyqtSignal()
    playingFailed = QtCore.pyqtSignal(str)
    refreshTimerSignal = QtCore.pyqtSignal(int)
    playingStopped = QtCore.pyqtSignal()

    def __init__(self, bluetoothService, playQueue):
        super().__init__()
        self.playQueue = playQueue
        self.bluetoothService = bluetoothService
        self.state = "IDLE"

        self.bluetoothService.disconnectedEndSignal.connect(self.onPlayingFinished)
        self.bluetoothService.connectedSignal.connect(self.onConnectedSignal)
        self.actualPlayInfo = None
        self.playService = PlayFileService(self)
        self.playService.finished.connect(self.onPlayingFinished)

        self.refreshTimer = QtCore.QTimer()
        self.refreshTimer.timeout.connect(self.onRefreshTimer)
        self.counter = 0

    def onRefreshTimer(self):
        self.counter = self.counter + 1
        self.refreshTimerSignal.emit(self.counter)

    def play(self, playQueueObject):
        if self.state == "IDLE":
            if isinstance(playQueueObject, BluetoothPlayQueueObject):
                self.state = "BLUETOOTH"
                self.actualPlayInfo = playQueueObject
                self.bluetoothService.connect(playQueueObject.macAddr(), playQueueObject.duration())

            if isinstance(playQueueObject, Mp3PlayQueueObject):
                self.state = "PLAYING"
                self.actualPlayInfo = playQueueObject
                self.playService.playMp3(playQueueObject.path())
                self.playingStarted.emit()
                self.counter = 0
                self.refreshTimer.start(1000)
        else:
            self.playQueue.addToPlayQueue(playQueueObject)

    def onConnectedSignal(self, exitCode):
        if exitCode == 1:
            self.playingFailed.emit(self.actualPlayInfo.name())
            self.state = "IDLE"
            self.onPlayingFinished()
        else:
            self.playingStarted.emit()
            self.counter = 0
            self.refreshTimer.start(1000)

    def onPlayingFinished(self):
        self.counter = 0
        self.refreshTimer.stop()

        self.actualPlayInfo = None
        self.state = "IDLE"
        if (self.playQueue.isEmpty()):
            self.playingStopped.emit()
        else:
            self.play(self.playQueue.popFromPlayQueue())

    def isPlaying(self):
        return self.state != "IDLE"

    def isPlayingFromBluetooth(self):
        return self.state == "BLUETOOTH"

    def getActualPlayingInfo(self):
       return self.actualPlayInfo

