#!/bin/bash
xhost local:root
docker run -it --rm \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v $(pwd)/blue-app:/src/blue-app \
    -e DISPLAY=$DISPLAY \
    blue-app
