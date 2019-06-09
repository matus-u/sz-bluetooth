#!/bin/bash

if [ $RUN_FROM_DOCKER ]; then

for i in ui/*; do pyuic5 $i -o generated/$(basename $i |cut -f 1 -d .).py; done;
python3 Main.py

else

    # start temperature check
    killall -9 start-temperature.sh
    scripts/./start-temperature.sh &

    # set volume
    amixer set 'Line In' 0
    amixer set 'Line Out' 100
    amixer set 'Mic1' 0
    amixer set 'Mic1 Boost' 0
    amixer set 'Mic2' 0
    amixer set 'Mic2 Boost' 0
    amixer set 'Mixer' 0
    amixer set 'Mixer Reversed' 0
    amixer set 'ADC Gain' 0
    amixer set 'DAC' 100
    amixer set 'DAC Reversed' off

    # configure touchscreen
    scripts/./stop-touch.sh
    sleep 1
    #scripts/./start-touch.sh $(dmesg | grep pl2303 | grep usb |tail -1 |  rev | cut -f 1 -d ' ' | rev)
    scripts/./start-touch.sh ttyUSB0
    sleep 1
    scripts/./calib-touch.sh

    # close blueman applet
    killall -9 blueman-applet

    #while true; do 
    for i in ui/*; do pyuic5 $i -o generated/$(basename $i |cut -f 1 -d .).py; done;
    python3 Main.py
    #done

fi

