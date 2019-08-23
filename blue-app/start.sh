#!/bin/bash

. generate-from-uic.sh

if [ $RUN_FROM_DOCKER ]; then

generate-from-uic
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
    DONE="1"
    while [ "$DONE" != "0" ] ; do
    scripts/./stop-touch.sh
    sleep 1
    #scripts/./start-touch.sh $(dmesg | grep pl2303 | grep usb |tail -1 |  rev | cut -f 1 -d ' ' | rev)
    scripts/./start-touch.sh ttyUSB0
    DONE="$?"
    sleep 1
    scripts/./calib-touch.sh
    done

    # close blueman applet
    killall -9 blueman-applet

    killall -9 sound-radio.py
    scripts/./sound-radio.py &
    
    #TODO TIMEZONE SET

    #while true; do 
    generate-from-uic
    python3 Main.py
    #done

fi

