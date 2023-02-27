#!/bin/bash

python manage.py migrate

echo "yes" | python manage.py collectstatic

celery -A misapi worker -l info &

gunicorn misapi.wsgi:application --bind 0.0.0.0:8000
