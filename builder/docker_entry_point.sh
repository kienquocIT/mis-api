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

# ==========================================
# 🔧 Dynamic Granian configuration
# ==========================================
CPU_CORES=$(nproc)
MEMORY_MB=$(grep MemTotal /proc/meminfo | awk '{print int($2/1024)}')

# Mỗi core chạy 2 worker, tối đa 8
WORKERS=$((CPU_CORES * 2))
if [ $WORKERS -gt 8 ]; then
  WORKERS=8
fi

# Threads ổn định = 2 mỗi worker
THREADS=2

echo "---------------------------------------"
echo "🧠 Server Info:"
echo "CPU cores: $CPU_CORES"
echo "Memory: ${MEMORY_MB}MB"
echo "Granian workers: $WORKERS"
echo "Threads per worker: $THREADS"
echo "---------------------------------------"

# ==========================================
# 🚀 Start Granian server
# ==========================================
exec granian --interface asgi \
  --host 0.0.0.0 \
  --port 8000 \
  --workers $WORKERS \
  --threads $THREADS \
  misapi.asgi:application
