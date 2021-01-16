FROM snakepacker/python:all as builder

COPY requirements.txt /mnt/

RUN python3.7 -m venv /usr/share/python3/venv && \
    /usr/share/python3/venv/bin/pip install -U pip && \
    /usr/share/python3/venv/bin/pip install -Ur /mnt/requirements.txt

FROM snakepacker/python:3.7 as base

RUN apt-get update && apt-get install 'ffmpeg' 'libsm6' 'libxext6' -y

COPY --from=builder /usr/share/python3/venv /usr/share/python3/venv

WORKDIR /home

RUN ["mkdir", "data_user"]
COPY MobileNetSSD ./MobileNetSSD
COPY src/ .
COPY deploy/entrypoint.sh ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]