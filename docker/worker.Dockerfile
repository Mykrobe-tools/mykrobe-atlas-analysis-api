ARG base_image=eu.gcr.io/atlas-275810/mykrobe-atlas-analysis-api
ARG tag=latest

FROM $base_image:$tag

RUN apt update

## Install Mykrobe atlas cli
RUN apt install -y --no-install-recommends libssl-dev libffi-dev dnsutils libz-dev
RUN git clone --branch v0.8.2 https://github.com/Mykrobe-tools/mykrobe.git mykrobe-predictor
WORKDIR /usr/src/app/mykrobe-predictor
RUN git clone --recursive -b geno_kmer_count https://github.com/Mykrobe-tools/mccortex && cd mccortex && make && cd ..
RUN pip install -r requirements.txt && python setup.py install
RUN ln -sf /usr/src/app/mykrobe-predictor/mccortex/bin/mccortex31 /usr/local/bin/mccortex31

## Install samtools
RUN apt install -y --no-install-recommends wget libncurses-dev
WORKDIR /usr/src/app
RUN wget https://github.com/samtools/samtools/releases/download/1.3.1/samtools-1.3.1.tar.bz2
RUN tar xf samtools-1.3.1.tar.bz2
WORKDIR samtools-1.3.1/
RUN make
WORKDIR ..
RUN cp -s samtools-1.3.1/samtools .
RUN cp -rp samtools-1.3.1/misc/plot-bamstats .

RUN apt clean
WORKDIR /usr/src/app
CMD celery -A app.celery worker -O fair -l DEBUG --concurrency=4 --uid=nobody