from django.urls import path

from apps.core.company.views import CompanyList, CompanyListOverview

urlpatterns = [
    path('list', CompanyList.as_view(), name='CompanyList'),
    path('overview', CompanyListOverview.as_view(), name='CompanyListOverview'),
]
