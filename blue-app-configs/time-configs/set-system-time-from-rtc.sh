#!/bin/bash

set -e

T=$(/opt/rtc-manipulate.py get | cut -f 2 -d = | head -c 12)
YY=20$(echo $T | head -c 2)
MONTH=$(echo $T | head -c 4 | tail -c 2)
DD=$(echo $T | head -c 6 | tail -c 2)
HH=$(echo $T | head -c 8 | tail -c 2)
MM=$(echo $T | head -c 10 | tail -c 2)
SS=$(echo $T | head -c 12 | tail -c 2)

TO_SET=$(date --date="TZ=\"UTC\" $YY-$MONTH-$DD $HH:$MM:$SS" +"%F %T")
timedatectl set-ntp false
timedatectl set-time "$TO_SET"
timedatectl set-ntp true

