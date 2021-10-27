from PyQt5 import QtCore
from PyQt5.QtCore import QRunnable, Qt, QThreadPool

class RunnableEmiter(QtCore.QObject):
    finished = QtCore.pyqtSignal()

class Runnable(QRunnable):

    def __init__(self, func):
        super().__init__()
        self.func = func
        self.emiter = RunnableEmiter()

    def run(self):
        self.func()
        self.emiter.finished.emit()
