FROM quay.io/biocontainers/mykrobe:0.8.2--py36h7e4d88f_0
RUN pip install --upgrade pip

RUN wget -O mykrobe-atlas-distance-client.zip https://github.com/Mykrobe-tools/mykrobe-atlas-distance-client/archive/master.zip
RUN unzip mykrobe-atlas-distance-client.zip && cd mykrobe-atlas-distance-client-master && python setup.py install && cd ..

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY requirements.txt /usr/src/app/requirements.txt
RUN pip install -r /usr/src/app/requirements.txt

COPY . /usr/src/app
WORKDIR /usr/src/app/
ENV FLASK_DEBUG=1
CMD uwsgi --http :80  --harakiri 300  --buffer-size=65535  -w wsgi