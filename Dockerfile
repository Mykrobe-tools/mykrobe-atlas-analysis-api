FROM python:3.6
RUN apt-get update -y && apt-get install -y libssl-dev libffi-dev dnsutils
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
RUN pip install --upgrade pip

## Install Mykrobe atlas cli
RUN git clone --branch v0.8.2 https://github.com/Mykrobe-tools/mykrobe.git mykrobe-predictor
WORKDIR /usr/src/app/mykrobe-predictor
RUN git clone --recursive -b geno_kmer_count https://github.com/Mykrobe-tools/mccortex && cd mccortex && make && cd ..
RUN pip install requests && pip install .
RUN ln -sf /usr/src/app/mykrobe-predictor/mccortex/bin/mccortex31 /usr/local/lib/python3.6/site-packages/mykrobe/cortex/mccortex31

RUN pip install git+https://github.com/Mykrobe-tools/mykrobe-atlas-distance-client.git

COPY requirements.txt /usr/src/app/requirements.txt
RUN pip install -r /usr/src/app/requirements.txt

COPY . /usr/src/app
WORKDIR /usr/src/app/
ENV FLASK_DEBUG=1
CMD uwsgi --http :80  --harakiri 300  --buffer-size=65535  -w wsgi