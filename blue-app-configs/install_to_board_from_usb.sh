#!/bin/bash

#scp configs/99-xelographics.rules root@$1:/etc/udev/rules.d/

#TODO INSTALL STEPS

##ALSO INSTALL KERNEL WITH elo SUPPORT!

apt-get install -y python3-pyqt5 pyqt5-dev-tools xserver-xorg-input-evdev inputattach xinput ofono python3-serial python3-pip
pip3 install --upgrade OPi.GPIO

cp 40-libinput.conf /usr/share/X11/xorg.conf.d/
cp start_usbstick.sh /opt/start_usbstick.sh
cp usb_start.desktop $(find /home -maxdepth 1 -mindepth 1 -type d  | tail -1)/.config/autostart/

cp time-configs/rtc-clock /etc/init.d/
cp time-configs/set-time-to-rtc.sh /opt/set-time-to-rtc.sh
cp time-configs/set-system-time-from-rtc.sh /opt/set-system-time-from-rtc.sh
cp time-configs/rtc-manipulate.py /opt/rtc-manipulate.py

pushd /etc/rc5.d/
ln -sf ../init.d/rtc-clock S02rtc-clock
popd

pushd /etc/rc6.d/
ln -sf ../init.d/rtc-clock K00rtc-clock
popd


