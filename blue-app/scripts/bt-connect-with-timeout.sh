#!/bin/bash

if [ "$1" == "" ];
then
	echo "Provide BT address please!"
	exit 1
fi

if [ "$2" == "" ];
then
	echo "Provide timeout please!"
	exit 1
fi

if [ $RUN_FROM_DOCKER ]; then
    sleep 5
    echo "PID"
    exit $(echo $RANDOM % 2 | bc)
fi

DEVICE=$1

function cleanup
{

kill -9 $1

bt-device -d "$DEVICE"
bt-device -r "$DEVICE"

rm -rf /tmp/bluetooth-connect-pipe

}



rm -rf /tmp/bluetooth-connect-pipe
mkfifo /tmp/bluetooth-connect-pipe

tail -f /tmp/bluetooth-connect-pipe | bt-device -c $DEVICE &
BT_DEVICE_PID=$!

PID=$(ps | grep tail  | cut -f 2 -d ' ')

sleep 1

echo "yes" >> /tmp/bluetooth-connect-pipe

wait $BT_DEVICE_PID
RETVAL=$?
if [ $RETVAL -ne 0 ]; then
	echo "Cannot connect to device $DEVICE"
	cleanup "$PID"
	exit $RETVAL
else
	echo "connect $DEVICE" | bluetoothctl
    echo "$PID"
fi

