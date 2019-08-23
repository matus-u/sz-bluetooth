#!/usr/bin/python3

import orangepi.pc
from time import sleep
import OPi.GPIO as GPIO

GPIO.setmode(orangepi.pc.BOARD)

class MuteState:

    NOT_MUTED = 0
    MUTED = 1

    def __init__(self):
        self.state = MuteState.NOT_MUTED

    def muteAction(self):
        if self.state == MuteState.NOT_MUTED:
            print ("MUTE")
            # TODO MUTE
            self.state = MuteState.MUTED
        else:
            print ("UNMUTE")
            # TODO UNMUTE
            self.state = MuteState.NOT_MUTED

muteStateHandler = MuteState()
def volume_mute(channel):
    muteStateHandler.muteAction()

GPIO.setup(27, GPIO.IN)
GPIO.add_event_detect(27, GPIO.RISING, callback=volume_mute)

def volume_up():
    print ("VOLUME UP")
    #TODO VOLUME UP

def volume_down():
    print ("VOLUME DOWN")
    #TODO VOLUME DOWN

GPIO_CONFIG = { 21 : volume_down, 22 : volume_up }
for num in GPIO_CONFIG:
    GPIO.setup(num, GPIO.IN)

try:
    while True:
        for num,callback in GPIO_CONFIG.items():
            if GPIO.input(num) == GPIO.HIGH:
                callback()
        sleep(0.15)
finally:
    GPIO.cleanup()

