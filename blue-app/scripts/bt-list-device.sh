#!/bin/bash
if [ $RUN_FROM_DOCKER ]; then
	sleep 1
	echo "FIRST DEVICE (30:j3:49:ng:34:jk)"
	echo "DEVICE (30:j3:49:ng:34:jk)"
	echo "DEVICE (30:j3:49:ng:34:jk)"
	echo "DEVICE (30:j3:49:ng:34:jk)"
	echo "FIFTH DEVICE (30:j3:49:ng:34:jk)"
	echo "SIXTH DEVICE (30:j3:49:ng:34:jk)"
	echo "SEVENTH DEVICE (30:j3:49:ng:34:jk)"
	echo "EIGHTH DEVICE (30:j3:49:ng:34:jk)"
	echo "NINE DEVICE (30:j3:49:ng:34:jk)"
else
	bt-device -l | tail +2
fi
