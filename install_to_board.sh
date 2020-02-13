#!/bin/bash

if [ "$1" == "" ];
then
	echo "Provide ip address of target device!"
	exit 1
fi

#TODO FIRST INSTALL TO UNKNOWN BOARD FROM USB WITH OTHER SCRIPT

sudo rm -rf blue-app/generated/*
sudo rm -rf blue-app/configs/*
pushd blue-app/scripts/
./generate-version.sh
popd
sudo find blue-app/ -name "__py*" | sudo xargs rm -rf
ssh root@$1 "rm -rf /media/usbstick/blue-app/" 
scp -r blue-app root@$1:/media/usbstick/
