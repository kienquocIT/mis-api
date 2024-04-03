from django.urls import path

from apps.core.tenant.views import (
    TenantPlanList,
    TenantDiagram,
)

urlpatterns = [
    path('tenant-plans', TenantPlanList.as_view(), name='TenantPlanList'),
    path('org-chart', TenantDiagram.as_view(), name='TenantDiagram'),
]
