from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

import orangepi.pc
import OPi.GPIO as GPIO

from services.LoggingService import LoggingService
from services import TimerService

class GpioHandler:
    def __init__(self, number):
        self.number = number
        self.previousState = GPIO.HIGH
        self.ignoreTicks = 0
        self.upCallbacks = []
        self.downCallbacks = []

    def evaluateLevel(self):
        if self.ignoreTicks == 0:
            actualState = GPIO.input(self.number)
            if self.previousState != actualState:
                self.previousState = actualState
                self.ignoreTicks = 10
                if actualState == GPIO.HIGH:
                    LoggingService.getLogger().info("ON GPIO " + str(self.number) + "UP")
                    for callback in self.upCallbacks:
                        callback()
                else:
                    LoggingService.getLogger().info("ON GPIO " + str(self.number) + "DOWN")
                    for callback in self.downCallbacks:
                        callback()
        else:
            self.ignoreTicks = self.ignoreTicks - 1;

    def addToUpCallbacks(self, callback):
        self.upCallbacks.append(callback)

    def addToDownCallbacks(self, callback):
        self.downCallbacks.append(callback)

class GpioService(TimerService.TimerStatusObject):

    RISING = "RISING"
    FALLING = "FALLING"

    def __init__(self):
        super().__init__(2)
        LoggingService.getLogger().info("GPIO - INIT")
        GPIO.setmode(orangepi.pc.BOARD)
        GPIO.setup(24, GPIO.IN)
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


        self.gpioHandlers = {
            24: GpioHandler(24),
            28: GpioHandler(28),
            29: GpioHandler(29),
            31: GpioHandler(31),
            33: GpioHandler(33),
            35: GpioHandler(35),
            37: GpioHandler(37),
        }

    def onTimeout(self):
        for num,handler in self.gpioHandlers.items():
            handler.evaluateLevel()

    def registerCallback(self, pin, trigger_type, callback):
        if trigger_type == GpioService.RISING:
            self.gpioHandlers[pin].addToUpCallbacks(callback)

        if trigger_type == GpioService.FALLING:
            self.gpioHandlers[pin].addToDownCallbacks(callback)

        LoggingService.getLogger().info("GPIO - REGISTER " + str(pin) + " " + str(trigger_type))

    def setGpio(self, pin, enable):
        GPIO.output(pin,enable)

    def cleanup(self):
        LoggingService.getLogger().info("GPIO - PRINT GPIO CLEANUP ")
