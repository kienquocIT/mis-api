from django.urls import path

from apps.core.tenant.views import TenantPlanList

urlpatterns = [
    path('tenant-plans', TenantPlanList.as_view(), name='TenantPlanList'),
]
