FROM quay.io/biocontainers/mykrobe:0.8.2--py36h7e4d88f_0
FROM python:3.6

RUN pip install git+https://github.com/Mykrobe-tools/mykrobe-atlas-distance-client.git

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY requirements.txt /usr/src/app/requirements.txt
RUN pip install -r /usr/src/app/requirements.txt

COPY . /usr/src/app
WORKDIR /usr/src/app/
ENV FLASK_DEBUG=1
CMD uwsgi --http :80  --harakiri 300  --buffer-size=65535  -w wsgi