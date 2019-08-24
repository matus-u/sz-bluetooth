#!/bin/bash

DIR=$(dirname "$0")

export LD_LIBRARY_PATH=$DIR:$LD_LIBRARY_PATH

$DIR/./gpio mode 14 out
$DIR/./gpio write 14 0

while true; do

TEMPERATURE=$(($(cat /sys/devices/virtual/thermal/thermal_zone0/temp) / 1000))

if [ "$TEMPERATURE" -gt 46 ]; then  
    $DIR/./gpio write 14 1
fi

if [ "$TEMPERATURE" -lt 41 ]; then  
    $DIR/./gpio write 14 0
fi

sleep 10

done
