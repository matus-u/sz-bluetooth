#!/bin/bash
if [ $RUN_FROM_DOCKER ]; then
	sleep 1
	echo "AP"
	echo "AP1"
	echo "AP2"
else
    nmcli device wifi list | tail -n +2 | tr -s ' '  | cut -f 2 -d ' ' 
fi
