#!/bin/bash

if [ "$1" == "" ];
then
	echo "Provide BT address please!"
	exit 1
fi

if [ $RUN_FROM_DOCKER ]; then
    echo $(echo $RANDOM % 255 | bc)
fi

RESPONSE=$(hcitool rssi $1 | cut -f 4 -d ' ')

if [ "$RESPONSE" == "Not connected." ]; then
    echo "NOT CONNECTED"
    exit 1
else
    if [ "$RESPONSE" == "0" ]; then
        echo 100
        exit 0
    fi
    echo "100-(($RESPONSE*100)/-255)" | bc
    exit 0
fi
