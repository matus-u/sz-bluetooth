#!/bin/bash
xhost local:root
docker run -it --rm \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v $(pwd)/blue-app:/src/blue-app \
    -v $(pwd)/settings:/src/blue-app-configs \
    -v $(pwd)/music:/src/music \
    -v /dev:/dev \
    -e DISPLAY=$DISPLAY \
    blue-app
