#!/bin/bash

if [ "$1" == "" ];
then
	echo "Provide touch screen device!"
	exit 1
fi

modprobe elo
sleep 1
inputattach --elotouch /dev/$1 --daemon
