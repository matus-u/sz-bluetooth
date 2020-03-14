#!/bin/bash

MAC=$(ifconfig eth0 | grep ether | tr -s ' ' | cut -f 3 -d ' ' | tr -s ':' '_')

mkdir -p ../blue-app-configs/images

if [ ${RUN_FROM_DOCKER} == "TRUE" ]; then
	. generate-from-uic.sh
	generate-from-uic
else
	echo "NOT"
fi

export LANG=C.UTF-8
python3 Main.py "[$MAC]"
