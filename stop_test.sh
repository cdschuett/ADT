#!/bin/bash

PID_FILE=~/processes/test.pid

if [ ! -f "$PID_FILE" ]; then
	echo "Error: $PID_FILE notfound."
	exit 1
fi

PID=$(cat "$PID_FILE")

if ! [[ "$PID" =~ ^[0-9]+$ ]]; then
	echo "Error: Invalid PID $PID found in $PID_FILE."
	exit 1
fi

echo "Killing process with $PID..."
kill "$PID"

if [ $? -eq 0 ]; then
	echo "Process killed gracefully..."
	rm "$PID_FILE"
else
	echo "Failed to kill test..."
	exit 1
fi
