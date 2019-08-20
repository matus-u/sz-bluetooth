#!/bin/bash
if [ $RUN_FROM_DOCKER ]; then
	sleep 1
	echo "AP"
	echo "AP1"
	echo "AP2"
else
    STATUS=$(nmcli device | grep wifi  | grep " connected ")
    if [ "$STATUS" == "" ]; then 
        exit 1
    else
        exit 0
    fi
fi
