# Builder
FROM python:3.6 AS builder

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip
RUN pip install wheel

WORKDIR /usr/src/app
COPY requirements.txt .
RUN pip install -r requirements.txt

# Runtime image
FROM python:3.6-slim
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN apt update && apt install -y --no-install-recommends libxml2 && apt clean

WORKDIR /usr/src/app
COPY . .
ENV FLASK_DEBUG=1
CMD uwsgi --http :80  --harakiri 300  --buffer-size=65535  -w wsgi:app