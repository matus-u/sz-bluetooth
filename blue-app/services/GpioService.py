from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

import orangepi.pc
import OPi.GPIO as GPIO

class GpioService:

    def __init__(self):
        print ("GPIO - INIT")
        GPIO.setmode(orangepi.pc.BOARD)

    def registerCallback(self, pin, callback):
        print ("GPIO - REGISTER " + str(pin))
        GPIO.setup(pin, GPIO.IN)
        GPIO.add_event_detect(pin, GPIO.RISING, callback=callback)

    def deregisterCallback(self, pin):
        print ("GPIO - DEREGISTER " + str(pin))
        GPIO.remove_event_detect(pin)

    def cleanup(self):
        print ("GPIO - PRINT GPIO CLEANUP ")
        GPIO.cleanup()
