from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

class TimerStatusObject(QtCore.QObject):

    startCheckStatus = QtCore.pyqtSignal()
    stopCheckStatus = QtCore.pyqtSignal()

    def __init__(self, duration):
        super().__init__()
        self.refreshTimer = QtCore.QTimer()
        self.duration = duration
        self.refreshTimer.timeout.connect(self.onTimeout)
        self.startCheckStatus.connect(lambda: self.refreshTimer.start(self.duration), QtCore.Qt.QueuedConnection)
        self.stopCheckStatus.connect(lambda: self.refreshTimer.stop(), QtCore.Qt.QueuedConnection)

    def start(self):
        self.startCheckStatus.emit()

    def stop(self):
        self.stopCheckStatus.emit()

    def onTimeout(self):
        pass


class TimerService:
    def __init__(self):
        self.thread = QtCore.QThread()
        self.thread.start()
    
    def addTimerWorker(self, timerStatusObject):
        timerStatusObject.moveToThread(self.thread)

    def quit(self):
        self.thread.quit()
        self.thread.wait()

