FROM python:3.6
RUN apt-get update -y
RUN apt-get install -y libssl-dev libffi-dev dnsutils
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
RUN pip install --upgrade pip
COPY . /usr/src/app

## Install Mykrobe atlas cli
RUN git clone -b 0.6.1 https://github.com/Mykrobe-tools/mykrobe.git mykrobe-predictor
WORKDIR /usr/src/app/mykrobe-predictor
RUN wget -O mykrobe-data.tar.gz https://bit.ly/2H9HKTU && tar -zxvf mykrobe-data.tar.gz && rm -fr src/mykrobe/data && mv mykrobe-data src/mykrobe/data
RUN pip install .



WORKDIR /usr/src/app/
RUN pip install -r requirements.txt
ENV FLASK_DEBUG=1
CMD flask run --port 8080