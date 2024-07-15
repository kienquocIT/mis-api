from django.urls import path

from apps.core.base.views import (
    PlanList, ApplicationPropertyList, ApplicationPropertyEmployeeList, PermissionApplicationList,
    TenantApplicationList,
    CountryList, CityList, DistrictList, WardList, BaseCurrencyList, BaseItemUnitList, IndicatorParamList,
    ApplicationPropertyOpportunityList, ApplicationDetail, ApplicationPropertyForPrintList,
    ApplicationPropertyForMailList, ZonesList, ZonesApplicationList, AppEmpConfigList,
)

urlpatterns = [
    path('location/countries', CountryList.as_view(), name='CountryList'),
    path('location/cities', CityList.as_view(), name='CityList'),
    path('location/districts', DistrictList.as_view(), name='DistrictList'),
    path('location/wards', WardList.as_view(), name='WardList'),
    path('currencies', BaseCurrencyList.as_view(), name='BaseCurrencyList'),

    path('plans', PlanList.as_view(), name='PlanList'),
    path('tenant-applications', TenantApplicationList.as_view(), name='TenantApplicationList'),
    path('application/<str:pk>', ApplicationDetail.as_view(), name='ApplicationDetail'),
    path('tenant-applications-property', ApplicationPropertyList.as_view(), name='ApplicationPropertyList'),
    path(
        'tenant-applications-property/print',
        ApplicationPropertyForPrintList.as_view(), name='ApplicationPropertyForPrintList'
    ),
    path(
        'tenant-applications-property/mail',
        ApplicationPropertyForMailList.as_view(), name='ApplicationPropertyForMailList'
    ),
    path(
        'applications-property-employee',
        ApplicationPropertyEmployeeList.as_view(),
        name='ApplicationPropertyEmployeeList'
    ),
    path('permissions', PermissionApplicationList.as_view(), name='PermissionApplicationList'),

    path('item-units', BaseItemUnitList.as_view(), name='BaseItemUnitList'),

    path('indicator-params', IndicatorParamList.as_view(), name='IndicatorParamList'),
    path(
        'applications-property-opportunity',
        ApplicationPropertyOpportunityList.as_view(),
        name='ApplicationPropertyOpportunityList'
    ),

    # zones
    path('zones-application/list', ZonesApplicationList.as_view(), name='ZonesApplicationList'),
    path('zones/list', ZonesList.as_view(), name='ZonesList'),
    # employee config on app
    path('app-emp-config/list', AppEmpConfigList.as_view(), name='AppEmpConfigList'),
]
