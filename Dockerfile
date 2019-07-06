FROM ubuntu:18.04

RUN apt-get update \
    && apt-get install -y \
      python3 \
      python3-pyqt5 \
      qtcreator \
      qt5-default \
      vim \
      bc \
      bash \
      pyqt5-dev-tools

WORKDIR /src

ENV RUN_FROM_DOCKER TRUE
