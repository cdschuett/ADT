#!/bin/bash

PID_FILE=~/processes/eicas.pid

export DISPLAY=:0
python /home/pi/Documents/py_test/ADT/eicas.py &

echo $! > "$PID_FILE"