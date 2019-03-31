FROM python:3.6
RUN apt-get update -y
RUN apt-get install -y libssl-dev libffi-dev dnsutils
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
RUN pip install --upgrade pip
COPY . /usr/src/app

## Install Mykrobe atlas cli
RUN git clone https://github.com/Mykrobe-tools/mykrobe.git mykrobe-predictor
WORKDIR /usr/src/app/mykrobe-predictor
RUN git checkout 9a818876de1b0db0b7f8f4399325e9a462a58573
RUN wget -O mykrobe-data.tar.gz https://bit.ly/2H9HKTU && tar -zxvf mykrobe-data.tar.gz && rm -fr src/mykrobe/data && mv mykrobe-data src/mykrobe/data
RUN pip install .



WORKDIR /usr/src/app/
RUN pip install -r requirements.txt
ENV FLASK_DEBUG=1
CMD flask run --port 8080