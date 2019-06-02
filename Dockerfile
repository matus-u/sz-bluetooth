FROM ubuntu:18.04

WORKDIR /src/blue-app

RUN apt-get update \
    && apt-get install -y \
      python3 \
      python3-pyqt5 \
      qtcreator \
      vim \
      pyqt5-dev-tools

