from django.urls import path

from apps.sales.purchasing.views import (
    PurchaseRequestList, PurchaseRequestDetail, PurchaseQuotationRequestList, PurchaseQuotationRequestDetail
)

# purchase request
urlpatterns = [
    path('purchase-request/list', PurchaseRequestList.as_view(), name='PurchaseRequestList'),
    path('purchase-request/<str:pk>', PurchaseRequestDetail.as_view(), name='PurchaseRequestDetail'),
] + [
    path(
        'purchase-quotation-request/list',
        PurchaseQuotationRequestList.as_view(),
        name='PurchaseQuotationRequestList'
    ),
    path(
        'purchase-quotation-request/<str:pk>',
        PurchaseQuotationRequestDetail.as_view(),
        name='PurchaseQuotationRequestDetail'
    ),
]
