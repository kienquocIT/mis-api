from django.urls import path
from apps.sales.cashoutflow.views import AdvancePaymentList, AdvancePaymentDetail, ReturnAdvanceList, \
    ReturnAdvanceDetail


urlpatterns = [
    path('advances-payments', AdvancePaymentList.as_view(), name='AdvancePaymentList'),
    path('advances-payments/<str:pk>', AdvancePaymentDetail.as_view(), name='AdvancePaymentDetail'),

    path('return-advances', ReturnAdvanceList.as_view(), name='ReturnAdvanceList'),
    path('return-advance/<str:pk>', ReturnAdvanceDetail.as_view(), name='ReturnAdvanceDetail')
]
