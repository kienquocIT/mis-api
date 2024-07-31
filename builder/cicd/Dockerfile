FROM python:3.11

ENV PYTHONUNBUFFERED=1

WORKDIR /code

COPY req.txt /code/

RUN python -m pip install -r req.txt

COPY . /code/
