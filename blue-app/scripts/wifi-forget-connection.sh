#!/bin/bash -
if [ $RUN_FROM_DOCKER ]; then
    sleep 1
    exit 0
fi

nmcli connection delete id "wifi_connect_name"

