FROM python:3.6-slim-buster
RUN apt-get update -y && apt-get install -y libssl-dev libffi-dev dnsutils git build-essential libz-dev && apt-get clean
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
RUN pip install --upgrade pip

COPY requirements.txt /usr/src/app/requirements.txt
RUN pip install -r /usr/src/app/requirements.txt

COPY . /usr/src/app
WORKDIR /usr/src/app/
ENV FLASK_DEBUG=1
CMD uwsgi --http :80  --harakiri 300  --buffer-size=65535  -w wsgi