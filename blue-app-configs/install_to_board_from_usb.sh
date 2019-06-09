#!/bin/bash

#scp configs/99-xelographics.rules root@$1:/etc/udev/rules.d/

#TODO INSTALL STEPS

##ALSO INSTALL KERNEL WITH elo SUPPORT!

apt-get install -y python3-pyqt5 pyqt5-dev-tools xserver-xorg-input-evdev inputattach xinput ofono

cp 40-libinput.conf /usr/share/X11/xorg.conf.d/
cp start_usbstick.sh /opt/start_usbstick.sh
cp usb_start.desktop $(find /home -maxdepth 1 -mindepth 1 -type d  | tail -1)/.config/autostart/

