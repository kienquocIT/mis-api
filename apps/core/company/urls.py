from django.urls import path
from apps.core.company.views import (
    CompanyList, CompanyDetail,
    CompanyListOverview, UserByCompanyOverviewDetail, EmployeeByCompanyOverviewDetail,
    CompanyLoginOfUserForOverviewDetail,
)

urlpatterns = [
    path('list', CompanyList.as_view(), name='CompanyList'),
    path('list/<str:pk>', CompanyDetail.as_view(), name='CompanyDetail'),

    # overview company page
    path('overview', CompanyListOverview.as_view(), name='CompanyListOverview'),
    path('overview/user/<str:company_id>', UserByCompanyOverviewDetail.as_view(), name='UserByCompanyOverviewDetail'),
    path(
        'overview/employee/<str:company_id>', EmployeeByCompanyOverviewDetail.as_view(),
        name='EmployeeByCompanyOverviewDetail'
    ),
    path(
        'overview/company-of-user/<str:company_id>', CompanyLoginOfUserForOverviewDetail.as_view(),
        name='CompanyLoginOfUserForOverviewDetail'
    ),

]
