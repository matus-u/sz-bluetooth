from PyQt5 import QtCore

from services import TimerService

class UpdateStatus(TimerService.TimerStatusObject):

    def __init__(self):
        super().__init__(3000)
        self.start()

    def onTimeout(self):
        QtCore.QProcess.startDetached("scripts/update-state.sh")

