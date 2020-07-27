FROM python:3.6-slim-buster
RUN apt-get update -y && apt-get install -y libssl-dev libffi-dev dnsutils git wget build-essential libz-dev && apt-get clean
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
RUN pip install --upgrade pip

## Install Mykrobe atlas cli
RUN git clone --branch v0.8.2 https://github.com/Mykrobe-tools/mykrobe.git mykrobe-predictor
WORKDIR /usr/src/app/mykrobe-predictor
RUN git clone --recursive -b geno_kmer_count https://github.com/Mykrobe-tools/mccortex && cd mccortex && make && cd ..
RUN pip install -r requirements.txt && python setup.py install
RUN ln -sf /usr/src/app/mykrobe-predictor/mccortex/bin/mccortex31 /usr/local/bin/mccortex31

## Install BIGSI
RUN wget -P /tmp http://download.oracle.com/berkeley-db/db-4.8.30.tar.gz && tar -xf /tmp/db-4.8.30.tar.gz -C /tmp && rm -f /tmp/db-4.8.30.tar.gz
RUN cd /tmp/db-4.8.30/build_unix && ../dist/configure && make && make install && cd /usr/src/app/
RUN git clone https://github.com/iqbal-lab-org/BIGSI.git /usr/src/app/BIGSI
WORKDIR /usr/src/app/BIGSI
RUN pip3 install -r requirements.txt && pip3 install -r optional-requirements.txt && pip3 install .

COPY requirements.txt /usr/src/app/requirements.txt
RUN pip install -r /usr/src/app/requirements.txt

COPY . /usr/src/app
WORKDIR /usr/src/app/
ENV FLASK_DEBUG=1
CMD uwsgi --http :80  --harakiri 300  --buffer-size=65535  -w wsgi