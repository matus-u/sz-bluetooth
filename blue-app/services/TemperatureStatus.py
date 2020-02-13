from PyQt5 import QtCore

from services import TimerService

import os

class TemperatureStatus(TimerService.TimerStatusObject):

    actualTemperature = QtCore.pyqtSignal(int)

    def __init__(self):
        super().__init__(3000)

    def onTimeout(self):
        if os.getenv('RUN_FROM_DOCKER', False) == False:
            try:
                with open("/sys/devices/virtual/thermal/thermal_zone0/temp") as f:
                    val = float(f.read()) / 1000
                    self.actualTemperature.emit(int(val))
            except:
                pass
        else:
            self.actualTemperature.emit(40)

