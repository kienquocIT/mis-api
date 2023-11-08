from django.conf import settings
from django.urls import path

from .views import DefaultDataStorageView, PlanApplicationConfigData

urlpatterns = [
    path('default-data', DefaultDataStorageView.as_view(), name='DefaultDataStorageView'),
    path('plan-app', PlanApplicationConfigData.as_view(), name='PlanApplicationConfigData'),
] if settings.SHOW_SYSTEM_DATA else []
