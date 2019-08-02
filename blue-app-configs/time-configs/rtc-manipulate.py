#!/usr/bin/python3

import sys, os, serial, time

if len(sys.argv) < 2 or len(sys.argv) > 3:
    print ("Wrong param count")
    print ("usage: ./rtc-manipulate.py get")
    print ("usage: ./rtc-manipulate.py set YYMMDDhhmmss")
    exit(1)

if sys.argv[1] != "get" and sys.argv[1] != "set":
    print ("Wrong paramter passed")
    print ("usage: ./rtc-manipulate.py get")
    print ("usage: ./rtc-manipulate.py set YYMMDDhhmmss")
    exit(1)

s = serial.Serial('/dev/ttyS3', baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=None, xonxoff=0, rtscts=0)

if sys.argv[1] == "set":
    if len(sys.argv) == 2:
        print ("Wrong param count")
        print ("usage: ./rtc-manipulate.py get")
        print ("usage: ./rtc-manipulate.py set YYMMDDhhmmss")
        exit(1)
    print ("Set part")
    toWrite = "U@ff00T="+sys.argv[2]+"3SS\r\n"
    print (toWrite)
    s.write(toWrite.encode())

else:
    s.write(b"U@ff00T?bfSS\r\n")
    serialString = s.readline().rstrip()
    print (serialString)
