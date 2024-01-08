from .celery import app as celery_app
from .load_env import load_env

__all__ = ('celery_app',)
