#!/bin/bash -
if [ $RUN_FROM_DOCKER ]; then
    exit $(echo $RANDOM % 2 | bc)
fi

nmcli --wait 30 --pretty  device wifi connect "$1" password "$2" name "wifi_connect_name"

exit $?
