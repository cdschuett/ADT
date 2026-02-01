#!/bin/bash

PID_FILE=~/processes/eicas.pid

openssl base64 -d -in eicas_signature.asc -out /tmp/eicas_sign.sha256
OUTPUT=$(openssl dgst -sha256 -verify ~/.identity/acft_id_public.pem -signature /tmp/eicas_sign.sha256 eicas.py)

if echo "$OUTPUT" | grep -q "Verified OK"; then

	export DISPLAY=:0
	python /home/pi/Documents/py_test/ADT/eicas.py &

	echo $! > "$PID_FILE"

else

	echo "Verification failed"
	echo "$OUTPUT"
	exit 1
	
fi
