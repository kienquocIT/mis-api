from django.urls import path
from apps.sales.servicequotation.views import (
    ServiceQuotationList, ServiceQuotationDetail)

urlpatterns = [
    path('list', ServiceQuotationList.as_view(), name='ServiceQuotationList'),
    path('detail/<str:pk>', ServiceQuotationDetail.as_view(), name='ServiceQuotationDetail'),
]
