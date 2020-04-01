##!/usr/bin/python3
#
#import orangepi.pc
#from time import sleep
#import OPi.GPIO as GPIO
#import os
#
#GPIO.setmode(orangepi.pc.BOARD)
#def volume_mute(channel):
#    os.system("amixer sset 'Line Out' toggle")
#
#GPIO.setup(27, GPIO.IN)
#GPIO.add_event_detect(27, GPIO.RISING, callback=volume_mute)
#
#def volume_up():
#    os.system("amixer sset 'Line Out' 1%+")
#
#def volume_down():
#    os.system("amixer sset 'Line Out' 1%-")
#
#GPIO_CONFIG = { 21 : volume_down, 22 : volume_up }
#for num in GPIO_CONFIG:
#    GPIO.setup(num, GPIO.IN)
#
#try:
#    while True:
#        for num,callback in GPIO_CONFIG.items():
#            if GPIO.input(num) == GPIO.HIGH:
#                callback()
#        sleep(0.15)
#finally:
#    GPIO.cleanup()
#
