#!/bin/bash

if [ "$1" == "" ];
then
	echo "Provide ip address of target device!"
	exit 1
fi

sudo rm -rf blue-app/generated/*
scp -r blue-app root@$1:/root/
scp configs/40-libinput.conf root@$1:/usr/share/X11/xorg.conf.d/
#scp configs/99-xelographics.rules root@$1:/etc/udev/rules.d/

#TODO INSTALL STEPS

#apt-get install python3-pyqt5
#apt-get install  pyqt5-dev-tools
