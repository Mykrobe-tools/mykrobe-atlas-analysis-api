ARG mykrobe_version=0.9.0
ARG bwa_version=3ddd7b87d41f89a404d95f083fb37c369f70d783
ARG samtools_version=1.3.1
ARG mccortex_version=geno_kmer_count

# Builder
FROM python:3.6 AS builder
ARG mykrobe_version
ARG bwa_version
ARG samtools_version
ARG mccortex_version

RUN apt-get update
RUN apt-get install -y --no-install-recommends dnsutils libz-dev

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip
RUN pip install wheel

# Build mccortex
WORKDIR /usr/src/app
RUN git clone --branch v${mykrobe_version} https://github.com/Mykrobe-tools/mykrobe.git mykrobe-predictor
WORKDIR mykrobe-predictor
RUN git clone --recursive -b ${mccortex_version} https://github.com/Mykrobe-tools/mccortex && cd mccortex && make

# Install Mykrobe into the current's Python environment
WORKDIR /usr/src/app/mykrobe-predictor
RUN pip install -r requirements.txt && python setup.py install

# Download Mykrobe panel data to current directory
RUN mykrobe panels update_metadata
RUN mykrobe panels update_species all

# Build samtools
WORKDIR /usr/src/app
RUN wget https://github.com/samtools/samtools/releases/download/${samtools_version}/samtools-${samtools_version}.tar.bz2 -O - | tar xfj -
RUN cd samtools-${samtools_version} && make

# Build bwa
WORKDIR /usr/src/app
RUN git clone https://github.com/lh3/bwa.git
WORKDIR bwa
RUN git checkout ${bwa_version}
RUN make

## Install berkeleydb
ENV BERKELEY_VERSION 4.8.30
# Download, configure and install BerkeleyDB
RUN wget -P /tmp http://download.oracle.com/berkeley-db/db-"${BERKELEY_VERSION}".tar.gz && \
    tar -xf /tmp/db-"${BERKELEY_VERSION}".tar.gz -C /tmp && \
    rm -f /tmp/db-"${BERKELEY_VERSION}".tar.gz
RUN cd /tmp/db-"${BERKELEY_VERSION}"/build_unix && \
    ../dist/configure && make && make install

# Python requirements
WORKDIR /usr/src/app
COPY requirements.txt .
RUN pip install -r requirements.txt

# Runtime image
FROM python:3.6-slim
ARG mykrobe_version
ARG bwa_version
ARG samtools_version
ARG mccortex_version

COPY --from=builder /usr/src/app/ /usr/src/app/
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Runtime dependencies
RUN apt update
RUN apt install -y --no-install-recommends gawk libssl-dev libffi-dev dnsutils libz-dev libncurses-dev
RUN apt clean

# Make symbolic links
WORKDIR /usr/src/app
RUN ln -s $(pwd)/mykrobe-predictor/mccortex/bin/mccortex31 /usr/local/bin/
RUN ln -s $(pwd)/samtools-${samtools_version}/samtools /usr/local/bin/
RUN ln -s $(pwd)/bwa-${bwa_version}/bwa /usr/local/bin/

ENV MYKROBE_VERSION=${mykrobe_version}
ENV BWA_VERSION=${bwa_version}
ENV SAMTOOLS_VERSION=${samtools_version}
ENV MCCORTEX_VERSION=${mccortex_version}

WORKDIR /usr/src/app
COPY . .
CMD celery -A app.celery worker -O fair -l DEBUG --concurrency=4 --uid=nobody