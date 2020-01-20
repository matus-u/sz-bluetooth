from PyQt5 import QtCore

from services import TimerService

class LedButtonService(TimerService.TimerStatusObject):

    LEFT = 7
    RIGHT = 12
    UP = 16
    DOWN = 18
    CONFIRM = 26

    def __init__(self, gpioService):
        super().__init__(500)

        self.gpioService = gpioService
        self.state = False

        self.buttonStates = {
            LedButtonService.LEFT : False,
            LedButtonService.RIGHT : False,
            LedButtonService.UP : False,
            LedButtonService.DOWN : False,
            LedButtonService.CONFIRM : False
        }

    def setButtonState(self, index, value):
        self.buttonStates[index] = value

    def onTimeout(self):
        for index, enabled in self.buttonStates.items():
            if not enabled:
                self.gpioService.setGpio(index, False)
            else:
                if self.state:
                    self.gpioService.setGpio(index, True)
                else:
                    self.gpioService.setGpio(index, False)

        self.state = not self.state
