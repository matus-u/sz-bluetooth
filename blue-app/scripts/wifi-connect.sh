#!/bin/bash -
if [ $RUN_FROM_DOCKER ]; then
    sleep 5
    exit $(echo $RANDOM % 2 | bc)
fi

STATUS=130

if [ "$2" == ""]; then
    nmcli --wait 30 --pretty  device wifi connect "$1" name "wifi_connect_name"
    STATUS=$?
else
    nmcli --wait 30 --pretty  device wifi connect "$1" password "$2" name "wifi_connect_name"
    STATUS=$?
fi

exit $STATUS
