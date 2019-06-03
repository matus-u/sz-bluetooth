#!/bin/bash
bt-device -l | tail +2 | cut -f 1 -d ' '
