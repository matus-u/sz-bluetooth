#!/bin/bash

if [ "$1" == "" ];
then
	echo "Provide BT address please!"
	exit 1
fi

if [ "$2" == "" ];
then
	echo "Provide PID please!"
	exit 1
fi

if [ $RUN_FROM_DOCKER ]; then
    sleep 2
    echo "DEVICE DISCONNECTED $1 $2"
    exit 0
fi

DEVICE=$1
PID=$2

function cleanup
{

kill -9 $PID

bt-device -d "$DEVICE"
bt-device -r "$DEVICE"

rm -rf /tmp/bluetooth-connect-pipe

}

cleanup
