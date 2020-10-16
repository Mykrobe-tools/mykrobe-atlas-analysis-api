ARG base_image=eu.gcr.io/atlas-275810/mykrobe-atlas-analysis-api
ARG tag=latest

FROM $base_image:$tag

RUN apt update
RUN apt install -y --no-install-recommends git build-essential wget gawk

## Install Mykrobe atlas cli
RUN apt install -y --no-install-recommends libssl-dev libffi-dev dnsutils libz-dev
WORKDIR /usr/src/app
RUN git clone --branch v0.8.2 https://github.com/Mykrobe-tools/mykrobe.git mykrobe-predictor
WORKDIR mykrobe-predictor
RUN git clone --recursive -b geno_kmer_count https://github.com/Mykrobe-tools/mccortex && cd mccortex && make
RUN pip install -r requirements.txt && python setup.py install
RUN ln -sf $(pwd)/mccortex/bin/mccortex31 /usr/local/bin/mccortex31

## Install samtools
RUN apt install -y --no-install-recommends libncurses-dev
WORKDIR /usr/src/app
RUN wget https://github.com/samtools/samtools/releases/download/1.3.1/samtools-1.3.1.tar.bz2
RUN tar xf samtools-1.3.1.tar.bz2 && cd samtools-1.3.1 && make
RUN ln -sf $(pwd)/samtools-1.3.1/samtools /usr/local/bin/

## Install bwa
WORKDIR /usr/src/app
RUN wget https://github.com/lh3/bwa/releases/download/v0.7.15/bwa-0.7.15.tar.bz2
RUN tar xf bwa-0.7.15.tar.bz2 && cd bwa-0.7.15 && make
RUN ln -sf $(pwd)/bwa-0.7.15/bwa /usr/local/bin/

# Assuming all indices are there as well
ENV REFERENCE_FILEPATH=data/NC_000962.3.fasta

RUN apt clean
WORKDIR /usr/src/app
COPY data data
CMD celery -A app.celery worker -O fair -l DEBUG --concurrency=4 --uid=nobody