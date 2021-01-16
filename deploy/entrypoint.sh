#!/bin/bash

. ../usr/share/python3/venv/bin/activate

read -r -p "Enter video name: " VIDEO
if [[ "${VIDEO}" == "" ]]
then
    echo "Error: video not found"
    exit 1
fi

export VIDEO="${VIDEO}"

python ./SaveDetection.py