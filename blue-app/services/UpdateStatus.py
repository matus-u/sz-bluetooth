from PyQt5 import QtCore

from services import TimerService
from services.LoggingService import LoggingService

class UpdateStatus(TimerService.TimerStatusObject):

    def __init__(self):
        super().__init__(10000)
        self.start()

    def onTimeout(self):
        LoggingService.getLogger().info("Update state to server")
        QtCore.QProcess.startDetached("scripts/update-state.sh")

