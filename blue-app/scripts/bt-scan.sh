#!/bin/bash
rm -rf /tmp/bluetooth-scan-pipe
mkfifo /tmp/bluetooth-scan-pipe

tail -f /tmp/bluetooth-scan-pipe | bluetoothctl &

PID=$(ps | grep tail  | cut -f 2 -d ' ')

echo "scan on" >> /tmp/bluetooth-scan-pipe

trap "{ echo quit >> /tmp/bluetooth-scan-pipe; kill -9 $PID; rm -rf /tmp/bluetooth-scan-pipe; exit 0; }" EXIT

while true; do
        sleep 100
done
