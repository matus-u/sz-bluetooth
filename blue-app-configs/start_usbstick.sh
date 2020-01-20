#!/bin/bash
                             

RUNLEVEL_VARIABLE=$(runlevel | cut -d ' ' -f2)
echo "reboot check: $RUNLEVEL_VARIABLE"
if [ "$RUNLEVEL_VARIABLE" == "6" ]; then
  echo "A reboot is in progress"
  exit 0
fi

FILES_USBSTICK="/media/usbstick/blue-app/start.sh"
if [ -e "$FILES_USBSTICK" ]; then
  echo "Usbstick is mounted..."
  sleep 10
  exit 0
fi


FILE_SDA1="/dev/sda1"
if [ -e "$FILE_SDA1" ]; then
  echo "/dev/sda1 exists"
  sudo umount "$FILE_SDA1"
fi

FILE_SDA="/dev/sda"
if [ -e "$FILE_SDA" ]; then
  echo "/dev/sda exists"
  sudo umount "$FILE_SDA"
fi

DIRECTORY="/media/usbstick"
if [ ! -d "$DIRECTORY" ]; then
  sudo mkdir "$directory"
fi

if [ -e "$FILE_SDA1" ]; then
  echo "mounting /dev/sda1 ..."
  sudo mount -o rw,exec,sync,iocharset=utf8 /dev/sda1 /media/usbstick
fi

if [ ! -e "$FILE_SDA1" ]; then
  echo "mounting /dev/sda ..."
  sudo mount -o rw,exec,sync,iocharset=utf8 /dev/sda /media/usbstick
fi

cd /media/usbstick

if [ -e "$FILES_USBSTICK" ]; then
    cd blue-app
    sudo ./start.sh
fi

sleep 100

exit 0
