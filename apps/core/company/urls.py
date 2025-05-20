from django.urls import path
from apps.core.company.views import (
    CompanyList,
    CompanyDetail, CompanyUploadLogo,
    CompanyListOverview,
    CompanyUserNotMapEmployeeList, CompanyOverviewDetail,
    CompanyConfigDetail, AccountingPoliciesDetail, CompanyFunctionNumberDetail,
)


urlpatterns = [
    path('config', CompanyConfigDetail.as_view(), name='CompanyConfigDetail'),
    path('function-number', CompanyFunctionNumberDetail.as_view(), name='CompanyFunctionNumberDetail'),
    path('accounting-policies-config', AccountingPoliciesDetail.as_view(), name='AccountingPoliciesDetail'),
    path('list', CompanyList.as_view(), name='CompanyList'),
    path('<str:pk>', CompanyDetail.as_view(), name='CompanyDetail'),
    path('<str:pk>/logo', CompanyUploadLogo.as_view(), name='CompanyUploadLogo'),

    # overview company page
    path('overview/list', CompanyListOverview.as_view(), name='CompanyListOverview'),
    path('overview/<str:pk>/<int:option>', CompanyOverviewDetail.as_view(), name='CompanyOverviewDetail'),
    path('user/available', CompanyUserNotMapEmployeeList.as_view(), name='CompanyUserNotMapEmployeeList'),
]
