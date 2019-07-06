#!/bin/bash

echo $1
if [ $RUN_FROM_DOCKER ]; then
    echo "DONE" ;	
else
    timedatectl set-timezone $1
fi
