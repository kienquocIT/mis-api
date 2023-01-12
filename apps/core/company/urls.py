from django.urls import path
from apps.core.company.views import (
    CompanyList, CompanyDetail,
    CompanyListOverview
)

urlpatterns = [
    path('list', CompanyList.as_view(), name='CompanyList'),
    path('list/<str:pk>', CompanyDetail.as_view(), name='CompanyDetail'),
    path('overview', CompanyListOverview.as_view(), name='CompanyListOverview'),
]
