from django.urls import path

from apps.core.tenant.views import TenantPlanList, TenantApplicationList

urlpatterns = [
    path('tenant-plans', TenantPlanList.as_view(), name='TenantPlanList'),
    path('tenant-application', TenantApplicationList.as_view(), name='TenantApplicationList'),
]
