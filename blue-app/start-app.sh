#!/bin/bash

MAC=$(ifconfig eth0 | grep ether | tr -s ' ' | cut -f 3 -d ' ' | tr -s ':' '_')

mkdir -p ../blue-app-configs/images
mkdir -p /tmp/logging

if [ "${RUN_FROM_DOCKER}" == "TRUE" ]; then
	. generate-from-uic.sh
	generate-from-uic

	pushd translation/
  ./release-languages.sh
	popd
fi

kill -9 $(pidof -x logger-remote.py)
scripts/./logger-remote.py "[$MAC]" "$(cat ../blue-app-configs/blue-app.conf  | grep MoneyServer | cut -f 2 -d =)" &

cd ..
cp -r blue-app /tmp/
cd /tmp/blue-app

export LANG=C.UTF-8
python3 Main.py "[$MAC]"
