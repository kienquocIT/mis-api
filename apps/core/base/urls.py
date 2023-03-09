from django.urls import path

from apps.core.base.views import PlanList, TenantApplicationList, ApplicationPropertyList, \
    ApplicationPropertyEmployeeList, PermissionApplicationList

urlpatterns = [
    path('plans', PlanList.as_view(), name='PlanList'),
    path('tenant-applications', TenantApplicationList.as_view(), name='TenantApplicationList'),
    path('tenant-applications-property', ApplicationPropertyList.as_view(), name='ApplicationPropertyList'),
    path(
        'applications-property-employee',
        ApplicationPropertyEmployeeList.as_view(),
        name='ApplicationPropertyEmployeeList'
    ),
    path('applications', ApplicationList.as_view(), name='ApplicationList'),
    path('permissions', PermissionApplicationList.as_view(), name='PermissionApplicationList'),
]
