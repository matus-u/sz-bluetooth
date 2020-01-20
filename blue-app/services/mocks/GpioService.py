from services.LoggingService import LoggingService

class GpioService:

    RISING = "RISING"
    FALLING = "FALLING"
    BOTH = "BOTH"

    def __init__(self):
        LoggingService.getLogger().info("GPIO - INIT")

    def registerCallback(self, trigger_type, pin, callback):
        LoggingService.getLogger().info("GPIO - REGISTER " + str(pin) + " " + trigger_type)

    def registerBothCallbacks(self, pin, callback):
        self.registerCallback("BOTH", pin, None)

    def deregisterCallback(self, pin):
        LoggingService.getLogger().info("GPIO - DEREGISTER " + str(pin))

    def setGpio(self, pin, enable):
        LoggingService.getLogger().info("SET GPIO - " + str(pin) + " " + str(enable))

    def cleanup(self):
        LoggingService.getLogger().info("GPIO - PRINT GPIO CLEANUP ")
