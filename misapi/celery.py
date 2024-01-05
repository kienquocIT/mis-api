import os

from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'misapi.settings')

app = Celery('misapi')

# @setup_logging.connect
# def config_loggers(*args, **kwargs):
#     from logging.config import dictConfig
#     from django.conf import settings
#     dictConfig(settings.LOGGING)


# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

app.conf.beat_schedule = {
    # Executes every 1minutes
    'modified-leave-available-every-new-year': {
        'task': 'apps.eoffice.leave.tasks.create_new_available_end_year',
        'schedule': crontab(minute=0, hour=0, day_of_month=1, month_of_year=1, day_of_week='*'),
    },
    'update-leave-available-each_month': {
        'task': 'apps.eoffice.leave.tasks.update_annual_leave_each_month',
        'schedule': crontab(minute=0, hour=0, day_of_month=15, month_of_year='*', day_of_week='*'),
    },
}
