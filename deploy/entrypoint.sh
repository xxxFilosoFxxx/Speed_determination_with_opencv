#!/bin/bash

. venv/bin/activate

read -r -p "Enter image name: " IMAGE
if [[ "${IMAGE}" == "" ]]
then
    echo "Error: image not found"
    exit 1
fi

export IMAGE="${IMAGE}"

python ./First_detection.py