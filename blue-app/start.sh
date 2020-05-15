#!/bin/bash



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

if [ -e /dev/ttyUSB0 ]; then
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
fi

# close blueman applet
killall -9 blueman-applet

#start blue-alsa
export LIBASOUND_THREAD_SAFE=0
bluealsa -p a2dp-sink 2> /dev/null &
bluealsa-aplay 00:00:00:00:00:00 2> /dev/null &

#while true; do
./start-app.sh
#done

echo "After application close"

while true; do
    sleep 100
done

