#!/bin/bash

DIR=$(dirname "$0")

export LD_LIBRARY_PATH=$DIR:$LD_LIBRARY_PATH

$DIR/./gpio mode 14 out

$DIR/./setup-ventilator.sh 0

sleep 1
$DIR/./setup-ventilator.sh 1
sleep 15
$DIR/./setup-ventilator.sh 0

while true; do

TEMPERATURE=$(($(cat /sys/devices/virtual/thermal/thermal_zone0/temp) / 1000))

if [ "$TEMPERATURE" -gt 46 ]; then  
    $DIR/./setup-ventilator.sh 1
fi

if [ "$TEMPERATURE" -lt 41 ]; then  
    $DIR/./setup-ventilator.sh 0
fi

sleep 10

done
