from django.urls import path
from apps.sales.financialcashflow.views import ARInvoiceListForCashInflow

urlpatterns = [
    path('ar-invoice-for-cashinflow/list', ARInvoiceListForCashInflow.as_view(), name='ARInvoiceListForCashInflow'),
]
