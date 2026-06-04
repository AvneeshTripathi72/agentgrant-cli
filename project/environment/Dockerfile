FROM python:3.11-slim@sha256:d8c0b852f5b61b365f57fc61f308a0ab9c90af44766c0d68f2ea8e7e10dfec1c

RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg tmux asciinema curl ca-certificates && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.lock /tmp/requirements.lock
RUN pip install --no-cache-dir --require-hashes --no-deps -r /tmp/requirements.lock

COPY *.py /app/
COPY audio/ /app/audio/

CMD ["/bin/bash"]
