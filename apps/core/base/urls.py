from django.urls import path

from apps.core.base.views import PlanList, TenantApplicationList, ApplicationPropertyList

urlpatterns = [
    path('plans', PlanList.as_view(), name='PlanList'),
    path('tenant-applications', TenantApplicationList.as_view(), name='TenantApplicationList'),
    path('tenant-applications-property', ApplicationPropertyList.as_view(), name='ApplicationPropertyList'),
]
