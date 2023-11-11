from django.urls import path

from .views import (ReportRevenueList, ReportProductList, ReportCustomerList)

urlpatterns = [
    path('revenue/list', ReportRevenueList.as_view(), name='ReportRevenueList'),
    path('product/list', ReportProductList.as_view(), name='ReportProductList'),
    path('customer/list', ReportCustomerList.as_view(), name='ReportCustomerList'),
]
