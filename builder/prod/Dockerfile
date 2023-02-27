FROM python:3.11

ENV PYTHONUNBUFFERED=1

WORKDIR /code

RUN apt-get update && \
    apt-get install -y python3-dev build-essential libssl-dev default-libmysqlclient-dev

COPY req.txt /code/

RUN python -m pip install -r req.txt

COPY . /code/
