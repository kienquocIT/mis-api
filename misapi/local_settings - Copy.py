DEBUG = True
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "mis_api",
        "USER": "root",
        "PASSWORD": "123456",
        "HOST": "127.0.0.1",
        "PORT": "3306",
        "OPTIONS": {
            # 'charset': 'utf8mb4',
            # "db_collation": "utf8mb4_unicode_ci",
            # "init_command": "SET GLOBAL regexp_time_limit=1024;",
        },
    },
}
SHOW_API_DOCS = True
# DEBUG = False
# # ALLOWED_HOSTS = ['*']
# ALLOWED_HOSTS = ['127.0.0.1']
# ALLOWED_CIDR_NETS = ['127.0.0.1']
# ALLOWED_IP_PROVISIONING = ['127.0.0.1']

# DEBUG_HIT_DB = True
# USE_CELERY_CONFIG_OPTION = 1
# CELERY_TASK_ALWAYS_EAGER = False
# USE_DATABASE_CONFIG_OPTION = 1

