from django.urls import path
from apps.sales.cashoutflow.views import (
    AdvancePaymentList, AdvancePaymentDetail,
    PaymentList, PaymentDetail,
    ReturnAdvanceList, ReturnAdvanceDetail, PaymentConfigList,
    AdvancePaymentCostList, PaymentCostList, APListForReturn, AdvancePaymentPrint, PaymentPrint
)
from apps.sales.cashoutflow.views.cashouflow_common import (
    CashOutflowQuotationList, CashOutflowSaleOrderList, CashOutflowSupplierList
)

urlpatterns = [
    path('quotation-list', CashOutflowQuotationList.as_view(), name='CashOutflowQuotationList'),
    path('sale-order-list', CashOutflowSaleOrderList.as_view(), name='CashOutflowSaleOrderList'),
    path('supplier-list', CashOutflowSupplierList.as_view(), name='CashOutflowSupplierList'),

    path('advance-payments', AdvancePaymentList.as_view(), name='AdvancePaymentList'),
    path('advance-payment/<str:pk>', AdvancePaymentDetail.as_view(), name='AdvancePaymentDetail'),
    path('advance-payment-cost-list/list', AdvancePaymentCostList.as_view(), name='AdvancePaymentCostList'),
    path('advance-payment-print/<str:pk>', AdvancePaymentPrint.as_view(), name='AdvancePaymentPrint'),

    path('payments', PaymentList.as_view(), name='PaymentList'),
    path('payment-config', PaymentConfigList.as_view(), name='PaymentConfigList'),
    path('payment/<str:pk>', PaymentDetail.as_view(), name='PaymentDetail'),
    path('payment-cost-list/list', PaymentCostList.as_view(), name='PaymentCostList'),
    path('payment-print/<str:pk>', PaymentPrint.as_view(), name='PaymentPrint'),

    path('return-advances', ReturnAdvanceList.as_view(), name='ReturnAdvanceList'),
    path('return-advance/<str:pk>', ReturnAdvanceDetail.as_view(), name='ReturnAdvanceDetail'),
    path('ap-list-for-return', APListForReturn.as_view(), name='APListForReturn'),
]
