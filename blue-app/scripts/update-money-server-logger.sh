#!/bin/bash
echo -n $1 > /tmp/money-server
kill -USR1 $(pidof -x logger-remote.py)

