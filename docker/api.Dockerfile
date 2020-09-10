FROM python:3.6-slim-buster

RUN apt-get update -y && apt-get install -y libssl-dev libffi-dev dnsutils git build-essential libz-dev && apt-get clean
RUN pip install --upgrade pip

WORKDIR /usr/src/app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
ENV FLASK_DEBUG=1
CMD uwsgi --http :80  --harakiri 300  --buffer-size=65535  -w wsgi