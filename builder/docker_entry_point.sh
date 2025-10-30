#!/bin/bash
set -e  # Dừng script nếu có lỗi xảy ra

#echo "🔄 Setting up message queue..."
#curl -i -u ${MSG_QUEUE_USER}:${MSG_QUEUE_PASSWORD} -X PUT "http://${MSG_QUEUE_HOST}:${MSG_QUEUE_API_PORT}/api/vhosts/${MSG_QUEUE_BROKER_VHOST}"

#echo "🔄 Initializing database..."
#python builder/init_db.py

echo "🔄 Check Django migrations..."
python manage.py makemigrations --check --dry-run --noinput

echo "🔄 Running Django migrations..."
python manage.py migrate

echo "🔄 Init data..."
python manage.py init_data

echo "🔄 MongoDB migrate..."
python manage.py mongo_migrate

echo "📦 Collecting static files..."
echo "yes" | python manage.py collectstatic --noinput

echo "🚀 Starting Celery workers..."
celery -A misapi worker --loglevel=info &

echo "📅 Starting Celery Beat scheduler..."
celery -A misapi beat --loglevel=info -S django &

#echo "🔥 Starting Gunicorn server..."
#exec gunicorn misapi.wsgi:application --bind 0.0.0.0:8000

echo "🔥 Starting Granian server..."
exec granian --interface wsgi --host 0.0.0.0 --port 8000 --workers 2 --access-log misapi.wsgi:application
