from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

from services.PlayFileService import PlayFileService
from model.PlayQueueObject import Mp3PlayQueueObject, BluetoothPlayQueueObject
from datetime import datetime
from services.LoggingService import LoggingService

class PlayLogicService(QtCore.QObject):

    playingInitialized = QtCore.pyqtSignal()
    playingStarted = QtCore.pyqtSignal()
    playingFailed = QtCore.pyqtSignal(str)
    refreshTimerSignal = QtCore.pyqtSignal(int)
    playingStopped = QtCore.pyqtSignal()

    PLAY_RETURN_QUEUE = 0
    PLAY_RETURN_IMMEDIATELLY = 1

    def __init__(self, bluetoothService, playQueue):
        super().__init__()
        self.playQueue = playQueue
        self.bluetoothService = bluetoothService
        self.state = "IDLE"

        self.bluetoothService.disconnectedEndSignal.connect(self.onPlayingFinished, QtCore.Qt.QueuedConnection)
        self.bluetoothService.connectedSignal.connect(self.onConnectedSignal, QtCore.Qt.QueuedConnection)
        self.actualPlayInfo = None
        self.playService = PlayFileService(self)
        self.playService.finished.connect(self.onPlayingFinished)

        self.refreshTimer = QtCore.QTimer()
        self.refreshTimer.timeout.connect(self.onRefreshTimer)
        self.counter = 0

        self.bluetoothConnectionTimer = QtCore.QTimer()
        self.bluetoothConnectionTimer.timeout.connect(lambda: self.bluetoothService.asyncDisconnect())

    def onRefreshTimer(self):
        self.counter = self.counter + 1
        self.refreshTimerSignal.emit(self.counter)

    def play(self, playQueueObject):
        if self.state == "IDLE":
            self.actualPlayInfo = playQueueObject
            if isinstance(playQueueObject, BluetoothPlayQueueObject):
                self.state = "BLUETOOTH"
                LoggingService.getLogger().info("Init bluetooth connect: " + playQueueObject.macAddr() + " " +  str(playQueueObject.duration()))
                self.bluetoothService.asyncConnect(playQueueObject.macAddr(), playQueueObject.duration())
                self.bluetoothConnectionTimer.setSingleShot(True)
                self.bluetoothConnectionTimer.start(playQueueObject.duration()*1000)
                self.playingInitialized.emit()

            if isinstance(playQueueObject, Mp3PlayQueueObject):
                self.state = "PLAYING"
                self.playService.playMp3(playQueueObject.path())
                self.playingInitialized.emit()
                self.playingStarted.emit()
                self.counter = 0
                self.refreshTimer.start(1000)

            self.actualPlayInfo.setStartTime(datetime.now())
            return PlayLogicService.PLAY_RETURN_IMMEDIATELLY
        else:
            if (self.playQueue.isEmpty()):
                playQueueObject.setStartTime(self.actualPlayInfo.endTime())
            else:
                playQueueObject.setStartTime(self.playQueue.getNextStartTime())

            self.playQueue.addToPlayQueue(playQueueObject)

            return PlayLogicService.PLAY_RETURN_QUEUE

    def onConnectedSignal(self, exitCode):
        if exitCode == 1:
            LoggingService.getLogger().info("Connection failed: %s" % str(self.actualPlayInfo.name()))
            self.playingFailed.emit(self.actualPlayInfo.name())
            if (self.bluetoothConnectionTimer.isActive()):
                self.bluetoothService.asyncConnect(self.actualPlayInfo.macAddr(), self.actualPlayInfo.duration())
            else:
                pass

        else:
            LoggingService.getLogger().info("Connection completed: %s" % str(self.actualPlayInfo.name()))
            self.bluetoothConnectionTimer.stop()
            self.playingStarted.emit()
            self.counter = 0
            self.refreshTimer.start(1000)

    def onPlayingFinished(self):
        self.counter = 0
        self.refreshTimer.stop()

        LoggingService.getLogger().info("Playing finished")

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

