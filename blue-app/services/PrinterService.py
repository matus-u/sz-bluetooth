import sys, serial
from datetime import datetime
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

class PrintingService(QtCore.QObject):

    def __init__(self):
        super().__init__()

        s = serial.Serial('/dev/ttyS2', baudrate=19200, bytesize=8, parity='N', stopbits=1, timeout=None, xonxoff=0, rtscts=0)
        s.write([0x1b, 0x40])
        s.write(b"\n")
        s.write(b"\n")
        s.write(b"\n")
        s.write(b"\n")
        s.write([0x1d, 0x56, 0])
        s.close()

    def printTicket(self, name, ID, winNumber):
        s = serial.Serial('/dev/ttyS2', baudrate=19200, bytesize=8, parity='N', stopbits=1, timeout=None, xonxoff=0, rtscts=0)

        s.write([0x1b, 0x40])
        s.write(datetime.now().strftime("%H:%M:%S         %d/%m/%Y\n").encode())
        s.write([0x1b, 0x4D, 49])
        s.write([0x1b, 0x4A, 10])
        s.write([0x1d, 0x21, 0x11])
        s.write(b"\n")
        s.write(b"      MUSICBOX\n")
        s.write(("         #"+ str(winNumber) +"\n").encode())
        s.write(b"\n")
        s.write([0x1d, 0x21, 0x00])
        s.write([0x1d, 0x21, 0x71])

        s.write(("DEVICE: " + name + "\n").encode())
        #s.write(b"ID:\n")
        s.write(b"\n")
        s.write(b"\n")
        s.write(b"\n")

        #CUT PAPER#
        s.write([0x1d, 0x56, 0])
        #s.write(b"\n")
        s.close()

