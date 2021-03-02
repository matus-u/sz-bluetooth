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

RUN apt-get update \
    && apt-get install -y \
    python3-requests \
    python3-pyqt5.qtwebsockets \
    python3-pyqt5.qtmultimedia \
    net-tools
RUN apt-get update \
    && apt-get install -y \
    qtvirtualkeyboard-plugin \
    qml-module-qtquick-virtualkeyboard \
    qml-module-qt-labs-folderlistmodel

RUN apt-get update \
    && apt-get install -y \
    locales \
    python3-mutagen

RUN apt-get update \
    && apt-get install -y \
    git

RUN apt-get update \
    && apt-get install -y \
    zip

RUN apt-get update \
    && apt-get install -y \
    gstreamer1.0-qt5 \
    libqt5multimedia5-plugins \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-libav

ENV RUN_FROM_DOCKER TRUE
