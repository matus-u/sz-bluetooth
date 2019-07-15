#!/bin/bash

MAC=$(ifconfig enp0s25 | grep ether | tr -s ' ' | cut -f 3 -d ' ' | tr : _)

wget --timeout=20 --method=PUT http://localhost:4000/api/devices/$MAC
