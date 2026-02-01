#!/bin/bash

cd ~/Documents/py_test/ADT

declare -A parts_list
parts_list["eicas_signature.asc"]="eicas.py"
parts_list["test_signature.asc"]="test_pattern.py"
parts_list["graphics_signature.asc"]="Graphics.py"
parts_list["constants_signature.asc"]="constants.py"

extension=".sha256"
RESULTS_FILE="verification_results.txt"
CURRENT_DATE=$(date +"%Y-%m-%d %H:%M:%S")

rm -rf ${RESULTS_FILE}

echo "[${CURRENT_DATE}] Part file verification executed on ${CURRENT_DATE}." > ${RESULTS_FILE}
echo "[${CURRENT_DATE}] Results are as follows:" >> ${RESULTS_FILE}

for key in "${!parts_list[@]}"; do
	openssl base64 -d -in "$key" -out /tmp/"${key}${extension}"
	OUTPUT=$(openssl dgst -sha256 -verify ~/.identity/acft_id_public.pem -signature /tmp/"${key}${extension}" ${parts_list[$key]})
	echo "[${CURRENT_DATE}] Part file ${parts_list[$key]} with signature file ${key} returned status as: ${OUTPUT}" >> ${RESULTS_FILE}

done

cat ${RESULTS_FILE} >> /home/pi/logs/mx_application.log
