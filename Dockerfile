FROM python:3.7-slim

RUN apt-get update && apt-get install 'ffmpeg' 'libsm6' 'build-essential' 'libxext6' 'cmake' -y

COPY requirements.txt /mnt/

RUN python3 -m pip install --upgrade pip && \
    pip install -Ur /mnt/requirements.txt

WORKDIR /home

RUN ["mkdir", "data_user"]
COPY MobileNetSSD ./MobileNetSSD
COPY src ./src
COPY save_detection.py ./save_detection.py
COPY deploy/entrypoint.sh ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
