from django.urls import path

from apps.core.base.views import (
    PlanList, ApplicationPropertyList, ApplicationPropertyEmployeeList, PermissionApplicationList,
    TenantApplicationList,
    CountryList, CityList, DistrictList, WardList,
)

urlpatterns = [
    path('location/countries', CountryList.as_view(), name='CountryList'),
    path('location/cities', CityList.as_view(), name='CityList'),
    path('location/districts', DistrictList.as_view(), name='DistrictList'),
    path('location/wards', WardList.as_view(), name='WardList'),

    path('plans', PlanList.as_view(), name='PlanList'),
    path('tenant-applications', TenantApplicationList.as_view(), name='TenantApplicationList'),
    path('tenant-applications-property', ApplicationPropertyList.as_view(), name='ApplicationPropertyList'),
    path(
        'applications-property-employee',
        ApplicationPropertyEmployeeList.as_view(),
        name='ApplicationPropertyEmployeeList'
    ),
    path('permissions', PermissionApplicationList.as_view(), name='PermissionApplicationList'),
]
