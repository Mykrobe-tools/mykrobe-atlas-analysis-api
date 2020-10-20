# These have to be on top
ARG base_image=eu.gcr.io/atlas-275810/mykrobe-atlas-analysis-api
ARG tag=latest

# Build dependencies
FROM python:3.6-slim-buster AS builder

RUN apt-get update
RUN apt-get install -y --no-install-recommends git build-essential wget libssl-dev libffi-dev dnsutils libz-dev libncurses-dev

# Build mccortex
WORKDIR /usr/src/app
RUN git clone --branch v0.9.0 https://github.com/Mykrobe-tools/mykrobe.git mykrobe-predictor
WORKDIR mykrobe-predictor
RUN git clone --recursive -b geno_kmer_count https://github.com/Mykrobe-tools/mccortex && cd mccortex && make

# Build samtools
WORKDIR /usr/src/app
RUN wget https://github.com/samtools/samtools/releases/download/1.3.1/samtools-1.3.1.tar.bz2
RUN tar xf samtools-1.3.1.tar.bz2 && cd samtools-1.3.1 && make
RUN rm samtools-1.3.1.tar.bz2

# Build bwa
WORKDIR /usr/src/app
RUN wget https://github.com/lh3/bwa/releases/download/v0.7.15/bwa-0.7.15.tar.bz2
RUN tar xf bwa-0.7.15.tar.bz2 && cd bwa-0.7.15 && make
RUN rm bwa-0.7.15.tar.bz2

# Build worker
FROM $base_image:$tag
COPY --from=builder /usr/src/app/ /usr/src/app/

# Runtime dependencies
RUN apt update
RUN apt install -y --no-install-recommends gawk libssl-dev libffi-dev dnsutils libz-dev libncurses-dev
RUN apt clean

# Install Mykrobe into the current's Python environment
WORKDIR /usr/src/app/mykrobe-predictor
RUN pip install -r requirements.txt && python setup.py install

# Download Mykrobe panel data
RUN mykrobe panels update_metadata
RUN mykrobe panels update_species all

# Make symbolic links
WORKDIR /usr/src/app
RUN ln -s $(pwd)/mykrobe-predictor/mccortex/bin/mccortex31 /usr/local/bin/
RUN ln -s $(pwd)/samtools-1.3.1/samtools /usr/local/bin/
RUN ln -s $(pwd)/bwa-0.7.15/bwa /usr/local/bin/

CMD celery -A app.celery worker -O fair -l DEBUG --concurrency=4 --uid=nobody