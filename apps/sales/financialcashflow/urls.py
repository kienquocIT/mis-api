from django.urls import path
from apps.sales.financialcashflow.views import (
    CashInflowList, CashInflowDetail,
    CustomerAdvanceListForCashInflow, ARInvoiceListForCashInflow,
    AdvanceForSupplierListForCashOutflow, APInvoiceListForCashOutflow
)

urlpatterns = [
    path('cashinflows', CashInflowList.as_view(), name='CashInflowList'),
    path('cashinflow/<str:pk>', CashInflowDetail.as_view(), name='CashInflowDetail'),
    path(
        'customer-advance-for-cashinflow/list',
        CustomerAdvanceListForCashInflow.as_view(),
        name='CustomerAdvanceListForCashInflow'
    ),
    path(
        'ar-invoice-for-cashinflow/list',
        ARInvoiceListForCashInflow.as_view(),
        name='ARInvoiceListForCashInflow'
    ),
] + [
    path(
        'advance-for-supplier-for-cashoutflow/list',
        AdvanceForSupplierListForCashOutflow.as_view(),
        name='AdvanceForSupplierListForCashOutflow'
    ),
    path(
        'ap-invoice-for-cashoutflow/list',
        APInvoiceListForCashOutflow.as_view(),
        name='APInvoiceListForCashOutflow'
    ),
]
