#!/bin/bash

# $1:
#   null: up
#   0: down

if [ -z "$1" ]
then
  echo "Docker Compose is running..."
  docker-compose --project-name api_dev --env-file env/.env.docker -f builder/dev-site/docker-compose.yml up --build -d
elif [ $1 = 0 ]
then
  echo "Docker Compose is downing..."
  docker-compose --project-name api_dev --env-file env/.env.docker -f builder/dev-site/docker-compose.yml down
fi
