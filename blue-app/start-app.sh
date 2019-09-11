#!/bin/bash

MAC=$(ifconfig eth0 | grep ether | tr -s ' ' | cut -f 3 -d ' ' | tr -s ':' '_')

. generate-from-uic.sh

generate-from-uic
python3 Main.py "[$MAC]"
