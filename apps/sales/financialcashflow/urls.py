from django.urls import path
from apps.sales.financialcashflow.views import (
    CashInflowList, CashInflowDetail,
    CustomerAdvanceListForCashInflow, ARInvoiceListForCashInflow,
    CashOutflowList, CashOutflowDetail,
    AdvanceForSupplierListForCOF, APInvoiceListForCOF
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
    path('cashoutflows', CashOutflowList.as_view(), name='CashOutflowList'),
    path('cashoutflow/<str:pk>', CashOutflowDetail.as_view(), name='CashOutflowDetail'),
    path(
        'advance-for-supplier-list-for-cof',
        AdvanceForSupplierListForCOF.as_view(),
        name='AdvanceForSupplierListForCOF'
    ),
    path(
        'ap-invoice-list-for-cof', APInvoiceListForCOF.as_view(), name='APInvoiceListForCOF'
    ),
]
