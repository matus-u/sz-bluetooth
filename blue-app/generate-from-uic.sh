#!/bin/bash

function generate-from-uic {
	rm -rf generated/*
	for i in ui/ui-design/*ui; do pyuic5 --resource-suffix='' --import-from=generated $i -o generated/$(basename $i |cut -f 1 -d .).py; done;
	for i in resources/compiled/*qrc; do pyrcc5 $i -o generated/$(basename $i |cut -f 1 -d .).py; done;
}
