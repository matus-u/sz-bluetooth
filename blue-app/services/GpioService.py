from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

import orangepi.pc
import OPi.GPIO as GPIO

from services.LoggingService import LoggingService

class GpioService:

    RISING = "RISING"
    FALLING = "FALLING"
    BOTH = "BOTH"

    def __init__(self):
        LoggingService.getLogger().info("GPIO - INIT")
        GPIO.setmode(orangepi.pc.BOARD)
        GPIO.setup(28, GPIO.IN)
        GPIO.setup(29, GPIO.IN)
        GPIO.setup(31, GPIO.IN)
        GPIO.setup(33, GPIO.IN)
        GPIO.setup(35, GPIO.IN)
        GPIO.setup(37, GPIO.IN)

        GPIO.setup( 7, GPIO.OUT)
        GPIO.setup(12, GPIO.OUT)
        GPIO.setup(16, GPIO.OUT)
        GPIO.setup(18, GPIO.OUT)
        GPIO.setup(26, GPIO.OUT)

        self.callbacks = {}

    def onGpio(self, channel):
        LoggingService.getLogger().info("ON GPIO " + str(channel) + " " + str(GPIO.input(channel) == GPIO.HIGH))
        self.callbacks[channel](GPIO.input(channel) == GPIO.HIGH)

    def registerCallback(self, trigger_type, pin, callback):
        trig_type = GPIO.BOTH
        if trigger_type == GpioService.RISING:
            trig_type = GPIO.RISING

        if trigger_type == GpioService.FALLING:
            trig_type = GPIO.FALLING

        LoggingService.getLogger().info("GPIO - REGISTER " + str(pin) + " " + str(trigger_type))
        GPIO.add_event_detect(pin, trig_type, callback=callback)

    def registerBothCallbacks(self, pin, callback):
        self.registerCallback(GpioService.BOTH, pin, self.onGpio)
        self.callbacks[pin] = callback

    def deregisterCallback(self, pin):
        LoggingService.getLogger().info("GPIO - DEREGISTER " + str(pin))
        GPIO.remove_event_detect(pin)

    def setGpio(self, pin, enable):
        GPIO.output(pin,enable)

    def cleanup(self):
        LoggingService.getLogger().info("GPIO - PRINT GPIO CLEANUP ")
        GPIO.cleanup()
