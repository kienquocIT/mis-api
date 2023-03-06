from django.urls import path

from apps.core.base.views import PlanList

urlpatterns = [
    path('plans', PlanList.as_view(), name='PlanList'),
]
