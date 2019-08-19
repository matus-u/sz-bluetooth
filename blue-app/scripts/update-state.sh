#!/bin/bash

DEV=eth0
if [ $RUN_FROM_DOCKER ]; then
    DEV=enp0s25
fi

#MAC=$(ifconfig $DEV | grep ether | tr -s ' ' | cut -f 3 -d ' ' | tr -s ':' '_')
#
#wget -O/dev/null --timeout=20 --method=PUT http://192.168.0.105:4000/api/devices/$MAC
