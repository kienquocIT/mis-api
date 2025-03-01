FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /code

RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

COPY req.txt /code/

RUN python -m pip install --no-cache-dir -r req.txt

COPY . /code/

RUN chmod +x /code/builder/docker_entry_point.sh

EXPOSE 8000

CMD ["/code/builder/docker_entry_point.sh"]

