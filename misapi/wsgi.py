"""
WSGI config for misapi project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from misapi.opentelemetry import init as open_telemetry_init
from misapi.mongo_client import MyMongoClient


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'misapi.settings')

open_telemetry_init()

MyMongoClient.check_connection()

application = get_wsgi_application()
