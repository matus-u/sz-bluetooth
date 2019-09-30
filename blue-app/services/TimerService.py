from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

class TimerStatusObject(QtCore.QObject):

    startCheckStatus = QtCore.pyqtSignal()
    stopCheckStatus = QtCore.pyqtSignal()

    def __init__(self, duration):
        super().__init__()
        self.duration = duration
        self.id = -1

    def start(self):
        self.startCheckStatus.emit()

    def stop(self):
        self.stopCheckStatus.emit()

    def startTimerSync(self):
        if self.id == -1:
            self.id = self.startTimer(self.duration, QtCore.Qt.PreciseTimer)

    def timerEvent(self, event):
        self.onTimeout()

    def stopTimerSync(self):
        if self.id != -1:
            self.killTimer(self.id)
        self.id = -1

    def onTimeout(self):
        pass

    def afterMove(self):
        pass

def addTimerWorker(timerStatusObject, thread):
        timerStatusObject.moveToThread(thread)
        timerStatusObject.afterMove()
        timerStatusObject.startCheckStatus.connect(timerStatusObject.startTimerSync, QtCore.Qt.QueuedConnection)
        timerStatusObject.stopCheckStatus.connect(timerStatusObject.stopTimerSync, QtCore.Qt.QueuedConnection)


class TimerService:
    def __init__(self):
        self.thread = QtCore.QThread()
        self.thread.start()
    
    def addTimerWorker(self, timerStatusObject):
        addTimerWorker(timerStatusObject, self.thread)

    def quit(self):
        self.thread.quit()
        self.thread.wait()

