#!/bin/bash

# $1:
#   null: up
#   0: down

arg_action="1"
arg_site="dev-site"

while getopts ":a:s:" opt; do
  case $opt in
    a)
      arg_action="$OPTARG"
      ;;
    s)
      arg_site="$OPTARG"
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
    :)
      echo "Option -$OPTARG requires an argument." >&2
      exit 1
      ;;
  esac
done

if [ "$arg_action" -eq "1" ]
then
  echo "Docker Compose is running..."
  docker-compose --project-name api_dev --env-file env/.env.docker -f builder/${arg_site}/docker-compose.yml up --build -d
elif [ "$arg_action" -eq "0" ]
then
  echo "Docker Compose is downing..."
  docker-compose --project-name api_dev --env-file env/.env.docker -f builder/${arg_site}/docker-compose.yml down
fi
