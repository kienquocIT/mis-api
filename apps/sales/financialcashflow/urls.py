from django.urls import path
from apps.sales.financialcashflow.views import (
    CashInflowList, CashInflowDetail,
    CustomerAdvanceListForCashInflow, ARInvoiceListForCashInflow,
    CashOutflowList, CashOutflowDetail,
    POPaymentStageListForCOF, APInvoicePOPaymentStageListForCOF
)
from apps.sales.financialcashflow.views.cof_views import SaleOrderExpenseListForCOF, SaleOrderForCOFList, \
    LeaseOrderExpenseListForCOF, LeaseOrderForCOFList

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
        'po-payment-stage-list-for-cof',
        POPaymentStageListForCOF.as_view(),
        name='POPaymentStageListForCOF'
    ),
    path(
        'ap-invoice-po-payment-stage-list-for-cof',
        APInvoicePOPaymentStageListForCOF.as_view(),
        name='APInvoicePOPaymentStageListForCOF'
    ),
    path(
        'so-list-for-cof',
        SaleOrderForCOFList.as_view(),
        name='SaleOrderForCOFList'
    ),
    path(
        'so-expense-list-for-cof',
        SaleOrderExpenseListForCOF.as_view(),
        name='SaleOrderExpenseListForCOF'
    ),
    path(
        'lo-list-for-cof',
        LeaseOrderForCOFList.as_view(),
        name='LeaseOrderForCOFList'
    ),
    path(
        'lo-expense-list-for-cof',
        LeaseOrderExpenseListForCOF.as_view(),
        name='LeaseOrderExpenseListForCOF'
    ),
]
