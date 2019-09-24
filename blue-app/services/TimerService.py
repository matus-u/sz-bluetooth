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

    def startTimerSync(self):
        self.refreshTimer.start(self.duration)

    def stopTimerSync(self):
        self.refreshTimer.stop()

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
        timerStatusObject.startCheckStatus.connect(timerStatusObject.startTimerSync, QtCore.Qt.QueuedConnection)
        timerStatusObject.stopCheckStatus.connect(timerStatusObject.stopTimerSync, QtCore.Qt.QueuedConnection)

    def quit(self):
        self.thread.quit()
        self.thread.wait()

