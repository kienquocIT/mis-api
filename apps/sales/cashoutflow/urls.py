from django.urls import path
from apps.sales.cashoutflow.views import (
    AdvancePaymentList, AdvancePaymentDetail,
    PaymentList, PaymentDetail,
    ReturnAdvanceList, ReturnAdvanceDetail, PaymentConfigList, AdvancePaymentCostList
)


urlpatterns = [
    path('advances-payments', AdvancePaymentList.as_view(), name='AdvancePaymentList'),
    path('advances-payments/<str:pk>', AdvancePaymentDetail.as_view(), name='AdvancePaymentDetail'),
    path('advances-payments-cost-list/lists', AdvancePaymentCostList.as_view(), name='AdvancePaymentCostList'),

    path('payments', PaymentList.as_view(), name='PaymentList'),
    path('payment-config', PaymentConfigList.as_view(), name='PaymentConfigList'),
    path('payments/<str:pk>', PaymentDetail.as_view(), name='PaymentDetail'),

    path('return-advances', ReturnAdvanceList.as_view(), name='ReturnAdvanceList'),
    path('return-advance/<str:pk>', ReturnAdvanceDetail.as_view(), name='ReturnAdvanceDetail'),
]
