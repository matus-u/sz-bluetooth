#!/bin/bash
function prepare-blue-app-dir {

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
}

prepare-blue-app-dir

if [ "$1" == "" ];
then
    echo "Generating package only in zip-packages"
    zip -r blue-app.zip blue-app
    mkdir -p zip-packages
    mv blue-app.zip zip-packages/
    exit 0
else
    echo "Sending to device: $1"
    ssh root@$1 "rm -rf /media/usbstick/blue-app/"
    scp -r blue-app root@$1:/media/usbstick/
fi

