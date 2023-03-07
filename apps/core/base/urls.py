from django.urls import path

from apps.core.base.views import PlanList, PermissionApplicationList, ApplicationList

urlpatterns = [
    path('plans', PlanList.as_view(), name='PlanList'),
    path('applications', ApplicationList.as_view(), name='ApplicationList'),
    path('permissions', PermissionApplicationList.as_view(), name='PermissionApplicationList'),
]
