from django.conf import settings
from django.urls import path

from .views import DefaultDataStorageView

urlpatterns = [
    path('default-data', DefaultDataStorageView.as_view(), name='DefaultDataStorageView'),
    path('application-config-data', DefaultDataStorageView.as_view(), name='DefaultDataStorageView'),
] if settings.SHOW_SYSTEM_DATA else []
