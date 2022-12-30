from django.urls import path

from apps.core.tenant.views import CompanyList

urlpatterns = [
    path('company', CompanyList.as_view(), name='CompanyList'),
]
