FROM python:3.6
RUN apt-get update -y
RUN apt-get install -y libssl-dev libffi-dev dnsutils
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
RUN pip install --upgrade pip
COPY . /usr/src/app

## Install Mykrobe atlas cli
RUN git clone -b api https://github.com/Mykrobe-tools/mykrobe-atlas-cli.git mykrobe-atlas-cli
WORKDIR /usr/src/app/mykrobe-atlas-cli
RUN wget -O mykrobe-data.tar.gz https://goo.gl/DXb9hN && tar -zxvf mykrobe-data.tar.gz && rm -fr src/mykrobe/data && mv mykrobe-data src/mykrobe/data
RUN pip install .



WORKDIR /usr/src/app/
RUN pip install -r requirements.txt
ENV FLASK_DEBUG=1
CMD flask run --port 8080