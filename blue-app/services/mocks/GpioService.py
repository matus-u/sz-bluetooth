from services.LoggingService import LoggingService

from services import TimerService

class GpioService(TimerService.TimerStatusObject):

    RISING = "RISING"
    FALLING = "FALLING"

    def __init__(self):
        super().__init__(20000)
        LoggingService.getLogger().info("GPIO - INIT")

    def registerCallback(self, pin, trigger_type, callback):
        LoggingService.getLogger().info("GPIO - REGISTER " + str(pin) + " " + trigger_type)

    def setGpio(self, pin, enable):
        LoggingService.getLogger().info("SET GPIO - " + str(pin) + " " + str(enable))

    def onTimeout(self, channel):
        LoggingService.getLogger().info("GPIO SERVICE TIMEOUT")

    def start(self):
        LoggingService.getLogger().info("GPIO SERVICE STARTED")

    def cleanup(self):
        LoggingService.getLogger().info("GPIO - PRINT GPIO CLEANUP ")
