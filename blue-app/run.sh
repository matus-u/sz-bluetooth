#!/bin/bash
for i in ui/*; do pyuic5 $i -o generated/$(basename $i |cut -f 1 -d .).py; done;
python3 Main.py

