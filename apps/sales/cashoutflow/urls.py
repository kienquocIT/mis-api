from django.urls import path
from apps.sales.cashoutflow.views import (
    AdvancePaymentList, AdvancePaymentDetail,
    PaymentList, PaymentDetail,
    ReturnAdvanceList, ReturnAdvanceDetail, PaymentConfigList,
    AdvancePaymentCostList, PaymentCostList, APListForReturn
)
from apps.sales.cashoutflow.views.cashouflow_common import CashOutflowQuotationList, CashOutflowSaleOrderList

urlpatterns = [
    path('quotation-list', CashOutflowQuotationList.as_view(), name='CashOutflowQuotationList'),
    path('sale-order-list', CashOutflowSaleOrderList.as_view(), name='CashOutflowSaleOrderList'),

    path('advances-payments', AdvancePaymentList.as_view(), name='AdvancePaymentList'),
    path('advances-payments/<str:pk>', AdvancePaymentDetail.as_view(), name='AdvancePaymentDetail'),
    path('advances-payments-cost-list/lists', AdvancePaymentCostList.as_view(), name='AdvancePaymentCostList'),

    path('payments', PaymentList.as_view(), name='PaymentList'),
    path('payment-config', PaymentConfigList.as_view(), name='PaymentConfigList'),
    path('payments/<str:pk>', PaymentDetail.as_view(), name='PaymentDetail'),
    path('payments-cost-list/lists', PaymentCostList.as_view(), name='PaymentCostList'),

    path('return-advances', ReturnAdvanceList.as_view(), name='ReturnAdvanceList'),
    path('return-advance/<str:pk>', ReturnAdvanceDetail.as_view(), name='ReturnAdvanceDetail'),
    path('ap-list-for-return', APListForReturn.as_view(), name='APListForReturn'),
]
