#!/bin/bash

set -e

/opt/rtc-manipulate.py set $(date --utc +%y%m%d%H%M%S)
