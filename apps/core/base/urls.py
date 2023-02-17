from django.urls import path

from apps.core.base.views import PlanList, TenantApplicationList

urlpatterns = [
    path('plans', PlanList.as_view(), name='PlanList'),
    path('tenant-applications', TenantApplicationList.as_view(), name='TenantApplicationList'),
]