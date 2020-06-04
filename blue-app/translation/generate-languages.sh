#!/bin/bash
pushd ../
. generate-from-uic.sh
generate-from-uic

popd

pylupdate5 -noobsolete ../ui/*py ../generated/*py ../services/*py ../*py -ts english.ts hungarian.ts slovak.ts polish.ts
