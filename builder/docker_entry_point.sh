#!/bin/bash
#python -m pylint --recursive=y .
curl -i -u ${MSG_QUEUE_USER}:${MSG_QUEUE_PASSWORD} -X PUT http://${MSG_QUEUE_HOST}:${MSG_QUEUE_API_PORT}/api/vhosts/${MSG_QUEUE_BROKER_VHOST}
python builder/init_db.py
python manage.py makemigrations --check --dry-run --noinput
python manage.py migrate
python manage.py init_data
echo "yes" | python manage.py collectstatic
celery -A misapi worker -l info &
gunicorn misapi.wsgi:application --bind 0.0.0.0:8000
