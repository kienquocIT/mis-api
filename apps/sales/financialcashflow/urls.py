from django.urls import path
from apps.sales.financialcashflow.views import (
    ARInvoiceListForCashInflow, SaleOrderListForCashInflow
)

urlpatterns = [
    path('ar-invoice-for-cashinflow/list', ARInvoiceListForCashInflow.as_view(), name='ARInvoiceListForCashInflow'),
    path('sale-order-for-cashinflow/list', SaleOrderListForCashInflow.as_view(), name='SaleOrderListForCashInflow'),
]
