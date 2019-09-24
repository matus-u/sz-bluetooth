from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

class TimerStatusObject(QtCore.QObject):

    startCheckStatus = QtCore.pyqtSignal()
    stopCheckStatus = QtCore.pyqtSignal()

    def __init__(self, duration):
        super().__init__()
        self.refreshTimer = QtCore.QTimer(parent=self)
        self.duration = duration

    def start(self):
        self.startCheckStatus.emit()

    def stop(self):
        self.stopCheckStatus.emit()

    def startSync(self):
        self.refreshTimer.start(self.duration)

    def stopSync(self):
        self.refreshTimer.stop()

    def onAsyncTimeout(self):
        self.asyncTimeout.emit()

    def onTimeout(self):
        pass

    def afterMove(self):
        pass


class TimerService:
    def __init__(self):
        self.thread = QtCore.QThread()
        self.thread.start()
    
    def addTimerWorker(self, timerStatusObject):
        timerStatusObject.moveToThread(self.thread)
        timerStatusObject.afterMove()
        timerStatusObject.refreshTimer.timeout.connect(timerStatusObject.onTimeout)
        timerStatusObject.startCheckStatus.connect(timerStatusObject.startSync, QtCore.Qt.QueuedConnection)
        timerStatusObject.stopCheckStatus.connect(timerStatusObject.stopSync, QtCore.Qt.QueuedConnection)

    def quit(self):
        self.thread.quit()
        self.thread.wait()

