FROM python:3.11

ENV PYTHONUNBUFFERED=1

WORKDIR /code

RUN apt-get update && apt-get install -y default-mysql-client curl

COPY req.txt /code/

RUN python -m pip install .

COPY . /code/
