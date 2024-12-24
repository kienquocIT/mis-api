from django.urls import path
from apps.sales.financialcashflow.views import (
    CashInflowList, CashInflowDetail,
    ARInvoiceListForCashInflow, CustomerListForCashInflow
)

urlpatterns = [
    path('cashinflows', CashInflowList.as_view(), name='CashInflowList'),
    path('cashinflow/<str:pk>', CashInflowDetail.as_view(), name='CashInflowDetail'),
    path('customer-for-cashinflow/list', CustomerListForCashInflow.as_view(), name='CustomerListForCashInflow'),
    path('ar-invoice-for-cashinflow/list', ARInvoiceListForCashInflow.as_view(), name='ARInvoiceListForCashInflow'),
]
