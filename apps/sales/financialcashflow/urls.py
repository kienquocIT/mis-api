from django.urls import path
from apps.sales.financialcashflow.views import CashInflowList, CashInflowDetail, ARInvoiceListForCashInflow

urlpatterns = [
    path('cashinflows', CashInflowList.as_view(), name='CashInflowList'),
    path('cashinflow/<str:pk>', CashInflowDetail.as_view(), name='CashInflowDetail'),
    path('ar-invoice-for-cashinflow/list', ARInvoiceListForCashInflow.as_view(), name='ARInvoiceListForCashInflow'),
]
