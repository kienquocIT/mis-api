# Mô tả các biến môi trường khi build repo này thành một web service

---

### Tập tin src/env/.env.docker
Sử dụng cho cấu hình container trên docker

```text
# docker
RUNNING_PORT=8020
```

---

### Tập tin src/.env
Sử dụng cho các giá trị trong mã nguồn code

```text
# general
SITE_NAME=API
ENABLE_PROD=1
SHOW_API_DOCS=0
DEBUG=0
ALLOWED_HOSTS=["api", "127.0.0.1", "localhost", ".bflow.vn"]

# queue
CELERY_TASK_ALWAYS_EAGER=0
MSG_QUEUE_HOST=queue_global
MSG_QUEUE_PORT=5672
MSG_QUEUE_API_PORT=15672
MSG_QUEUE_USER=rabbitmq_user
MSG_QUEUE_PASSWORD=rabbitmq_passwd
MSG_QUEUE_BROKER_VHOST=/

# db
DB_HOST=mysql_db_global
DB_PORT=3306
DB_NAME=sit_api
DB_USER=mysql-local
DB_PASSWORD=p@ssw0rd

# cache
CACHE_ENABLED=1
CACHE_KEY_PREFIX=sit_api
CACHE_HOST=memcached_global
CACHE_PORT=11211

# email
EMAIL_SERVER_DEFAULT_HOST=mail.bflow.vn
EMAIL_SERVER_DEFAULT_PORT=587
EMAIL_SERVER_DEFAULT_USERNAME=test@bflow.vn
EMAIL_SERVER_DEFAULT_PASSWORD=p@ssw0rd
EMAIL_SERVER_DEFAULT_USE_TLS=1
EMAIL_SERVER_DEFAULT_USE_SSL=0
EMAIL_SERVER_DEFAULT_REPLY=info@mtsolution.com.vn
EMAIL_SERVER_DEFAULT_CC=[]
EMAIL_SERVER_DEFAULT_BCC=[]

# telegram
TELEGRAM_TOKEN=t0k3n
TELEGRAM_CHAT_ID=ch@t1d

# ui domain
UI_DOMAIN_SUFFIX=.bflow.vn
UI_DOMAIN_PROTOCOL=https

# jaeger trace
ENABLE_TRACING=1
JAEGER_TRACING_HOST=jaeger_global
JAEGER_TRACING_PORT=6831
JAEGER_TRACING_PROJECT_NAME=API

# mongodb
MONGO_HOST=mongo_db_global
MONGO_PORT=27017
MONGO_USERNAME=root
MONGO_PASSWORD=p@ssw0rd
MONGO_DB_NAME=bflow

# 2fa
SYNC_2FA_ENABLED=1
PASSWORD_TOTP_2FA=totp-*

# throttling: misapi.throttling
THROTTLE_AUTH=200
THROTTLE_ANON=50
```
