#!/bin/bash
modprobe elo
inputattach --elotouch /dev/$1 --daemon
/root/blue-app/scripts/calib-touch.sh
