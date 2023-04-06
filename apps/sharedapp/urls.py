from django.urls import path

from .views import DefaultDataStorageView

urlpatterns = [
    path('default-data', DefaultDataStorageView.as_view(), name='DefaultDataStorageView'),
]
