from services.LoggingService import LoggingService

class GpioService:
    def __init__(self):
        LoggingService.getLogger().info("GPIO - INIT")

    def registeCallback(self, trigger_type, pin, callback):
        LoggingService.getLogger().info("GPIO - REGISTER " + str(pin) + " " + trigger_type)

    def registerBothCallbacks(self, pin, callback):
        self.registeCallback("BOTH", pin, None)

    def deregisterCallback(self, pin):
        LoggingService.getLogger().info("GPIO - DEREGISTER " + str(pin))

    def cleanup(self):
        LoggingService.getLogger().info("GPIO - PRINT GPIO CLEANUP ")
