#!/bin/bash
xhost local:root
docker run -it --rm \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v $(pwd)/blue-app:/src/blue-app \
    -v $(pwd)/settings:/src/blue-app-configs \
    -v $(pwd)/.git:/src/.git \
    -v $(pwd)/music:/src/music \
    -v $(pwd)/install_to_board.sh:/src/install_to_board.sh \
    -v /dev:/dev \
    -e DISPLAY=$DISPLAY \
    blue-app
