#!/bin/bash
if [ $RUN_FROM_DOCKER ]; then
	exit 0
else
    timedatectl set-timezone $1
fi
