from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

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
        self.bluetoothService.refreshTimerSignal.connect(lambda val: self.refreshTimerSignal.emit(val))
        self.bluetoothService.connectedSignal.connect(self.onConnectedSignal)

    def playFromBluetooth(self, macAddr, duration):
        if self.state == "IDLE":
            print ("PLAY FROM BLUETOOTH")
            self.bluetoothService.connect(macAddr, duration)
            self.state = "BLUETOOTH"
        else:
            print("ERROR")

    def startPlaying(self, mp3info):
        self.state = "PLAYING"
        #TODO PLAY CODE
        self.playingStarted.emit()
            
    def playFromLocal(self, mp3info):
        if self.state == "IDLE":
            self.startPlaying(mp3info)
        else:
            self.playQueue.addToPlayQueue(mp3info)

    def onConnectedSignal(self, exitCode):
        print ("ON CONNECTED SIGNAL ")
        if exitCode == 1:
            self.playingFailed.emit()
            self.state = "IDLE"
        else:
            self.playingStarted.emit()

    def onPlayingFinished(self):
        print ("ON PLAYING FINISHED ")
        if (self.playQueue.isEmpty()):
            self.playingStopped.emit()
            self.state = "IDLE"
        else:
            self.startPlaying(self.playQueue.popFromPlayQueue())

    def isPlaying(self):
        return self.state != "IDLE"

    def isPlayingFromBluetooth(self):
        return self.state == "BLUETOOTH"

