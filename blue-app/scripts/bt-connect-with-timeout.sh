#!/bin/bash

if [ "$1" == "" ]; 
then 
	echo "Provide BT address please!"
	exit 1
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

ps | grep bt-device

PID=$(ps | grep tail  | cut -f 2 -d ' ')

sleep 1

echo "yes" >> /tmp/bluetooth-connect-pipe

wait $BT_DEVICE_PID
RETVAL=$?
if [ $RETVAL -ne 0 ]; then
	echo "Cannot connect to device $DEVICE"
	cleanup "$PID" ""
	exit $RETVAL
else
	echo "connect $DEVICE" | bluetoothctl
fi

sleep 20

cleanup "$PID"


