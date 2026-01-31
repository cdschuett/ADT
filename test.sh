#!/bin/bash

PID_FILE=~/processes/test.pid

export DISPLAY=:0
python /home/pi/Documents/py_test/ADT/test_pattern.py &

echo $! > "$PID_FILE"