from django.urls import path

from apps.core.tenant.views import (
    TenantPlanList,
    TenantApps,
)

urlpatterns = [
    path('tenant-plans', TenantPlanList.as_view(), name='TenantPlanList'),
    path('tenant-plans/apps', TenantApps.as_view(), name='TenantApps'),
]
