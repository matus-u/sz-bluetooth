from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

import orangepi.pc
import OPi.GPIO as GPIO

from services.LoggingService import LoggingService

class GpioService:

    def __init__(self):
        LoggingService.getLogger().info("GPIO - INIT")
        GPIO.setmode(orangepi.pc.BOARD)
        GPIO.setup(37, GPIO.IN)
        self.callbacks = {}

    def onGpio(self, channel):
        self.callbacks[channel](GPIO.input(channel) == GPIO.HIGH)

    def registeCallback(self, trigger_type, pin, callback):
        LoggingService.getLogger().info("GPIO - REGISTER " + str(pin) + " " + str(trigger_type))
        GPIO.add_event_detect(pin, trigger_type, callback=callback)

    def registerBothCallbacks(self, pin, callback):
        self.registeCallback(GPIO.BOTH, pin, self.onGpio)
        self.callbacks[pin] = callback

    def deregisterCallback(self, pin):
        LoggingService.getLogger().info("GPIO - DEREGISTER " + str(pin))
        GPIO.remove_event_detect(pin)

    def cleanup(self):
        LoggingService.getLogger().info("GPIO - PRINT GPIO CLEANUP ")
        GPIO.cleanup()
