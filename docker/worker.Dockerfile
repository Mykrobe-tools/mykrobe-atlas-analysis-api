FROM eu.gcr.io/atlas-275810/mykrobe-atlas-analysis-api:latest

## Install Mykrobe atlas cli
RUN git clone --branch v0.8.2 https://github.com/Mykrobe-tools/mykrobe.git mykrobe-predictor
WORKDIR /usr/src/app/mykrobe-predictor
RUN git clone --recursive -b geno_kmer_count https://github.com/Mykrobe-tools/mccortex && cd mccortex && make && cd ..
RUN pip install -r requirements.txt && python setup.py install
RUN ln -sf /usr/src/app/mykrobe-predictor/mccortex/bin/mccortex31 /usr/local/bin/mccortex31