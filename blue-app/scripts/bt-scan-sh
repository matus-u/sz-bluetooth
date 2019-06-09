#!/bin/bash
if [ $RUN_FROM_DOCKER ]; then
	sleep 1
else
	rm -rf /tmp/bluetooth-scan-pipe
	mkfifo /tmp/bluetooth-scan-pipe

	tail -f /tmp/bluetooth-scan-pipe | bluetoothctl &

	PID=$(ps | grep tail  | cut -f 2 -d ' ')

	echo "scan on" >> /tmp/bluetooth-scan-pipe

	sleep 12

	echo "scan off" >> /tmp/bluetooth-scan-pipe

	echo "quit" >> /tmp/bluetooth-scan-pipe

	sleep 1

	kill -9 $PID

	rm -rf /tmp/bluetooth-scan-pipe
fi
