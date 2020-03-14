#!/bin/bash

if [ "$1" == "" ];
then
	echo "Provide ip address of target device!"
	exit 1
fi

#TODO FIRST INSTALL TO UNKNOWN BOARD FROM USB WITH OTHER SCRIPT

rm -rf blue-app/generated/*
rm -rf blue-app/configs/*

pushd blue-app/scripts/
./generate-version.sh
popd

pushd blue-app/
. generate-from-uic.sh
generate-from-uic
popd

find blue-app/ -name "__py*" | xargs rm -rf
ssh root@$1 "rm -rf /media/usbstick/blue-app/" 
scp -r blue-app root@$1:/media/usbstick/
