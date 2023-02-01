from django.urls import path
from apps.core.company.views import (
    CompanyList,
    CompanyDetail,
    CompanyListOverview,
    CompanyUserNotMapEmployeeList
)

urlpatterns = [
    path('list', CompanyList.as_view(), name='CompanyList'),
    path('list/<str:pk>', CompanyDetail.as_view(), name='CompanyDetail'),

    # overview company page
    path('overview', CompanyListOverview.as_view(), name='CompanyListOverview'),
    path('user-available', CompanyUserNotMapEmployeeList.as_view(), name='CompanyUserNotMapEmployeeList'),
]
