#!/bin/bash

. venv/bin/activate

read -r -p "Enter video name: " VIDEO
if [[ "${VIDEO}" == "" ]]
then
    echo "Error: video not found"
    exit 1
fi

export VIDEO="${VIDEO}"

python ./First_detection.py