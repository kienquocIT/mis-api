from django.urls import path

from apps.core.company.views import CompanyList

urlpatterns = [
    path('list', CompanyList.as_view(), name='CompanyList'),
]
