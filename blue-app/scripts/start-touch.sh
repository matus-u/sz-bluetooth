#!/bin/bash

if [ "$1" == "" ];
then
	echo "Provide touch screen device!"
	exit 1
fi

modprobe elo
sleep 1
inputattach --elotouch /dev/$1 --daemon
sleep 1
RET=$([ "$(dmesg | tail | grep "elo serio2")" != "" ] && echo 0 || echo 1)
echo "INPUTATTACH $RET"
sleep 1
exit $RET
