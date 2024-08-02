#!/bin/bash

# $1:
#   null: up
#   0: down

if [ $2 == "1" ]
then
  echo "Docker Compose is running..."
  docker-compose --project-name api_$1 --env-file env/.env.docker -f builder/$1-site/docker-compose.yml up --build -d
elif [ $2 == "0" ]
then
  echo "Docker Compose is downing..."
  docker-compose --project-name api_$1 --env-file env/.env.docker -f builder/$1-site/docker-compose.yml down
else
  echo "args: \$1{site|dev|uat|prod} \$2{0|1}"
  echo "Not support: $2"
fi
