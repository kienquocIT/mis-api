from django.urls import path

from .views import (
    DiagramList
)

urlpatterns = [
    path('list', DiagramList.as_view(), name='DiagramList'),
]
