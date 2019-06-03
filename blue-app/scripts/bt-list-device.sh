#!/bin/bash
if [ $RUN_FROM_DOCKER == "TRUE" ]; then
	sleep 1
	echo "FIRST DEVICE"
	echo "SECOND DEVICE"
	echo "THIRD DEVICE"
	echo "FOURTH DEVICE"
	echo "FIFTH DEVICE"
	echo "SIXTH DEVICE"
	echo "SEVENTH DEVICE"
	echo "EIGHTH DEVICE"
	echo "NINE DEVICE"
else
	bt-device -l | tail +2 | cut -f 1 -d ' '
fi
