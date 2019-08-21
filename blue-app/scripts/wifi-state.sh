#!/bin/bash
if [ $RUN_FROM_DOCKER ]; then
    exit $(echo $RANDOM % 2 | bc)
else
    STATUS=$(nmcli device | grep wifi  | grep " connected ")
    if [ "$STATUS" == "" ]; then 
        exit 1
    else
        exit 0
    fi
fi
