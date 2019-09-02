#!/bin/bash

function generate-from-uic {
	rm -rf generated/*
	for i in ui/*; do pyuic5 $i -o generated/$(basename $i |cut -f 1 -d .).py; done;
	for i in resources/*qrc; do pyrcc5 $i -o generated/$(basename $i |cut -f 1 -d .).py; done;
}
