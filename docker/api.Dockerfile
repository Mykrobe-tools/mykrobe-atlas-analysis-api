# Dependencies
FROM python:3.6-slim-buster AS builder

RUN apt-get update && apt-get install -y --no-install-recommends git build-essential

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip

WORKDIR /usr/src/app
COPY requirements.txt .
RUN pip install -r requirements.txt

# App
FROM python:3.6-slim-buster
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /usr/src/app
COPY . .
ENV FLASK_DEBUG=1
CMD uwsgi --http :80  --harakiri 300  --buffer-size=65535  -w wsgi:app