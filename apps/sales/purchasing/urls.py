from django.urls import path

from apps.sales.purchasing.views import (
    PurchaseRequestList, PurchaseRequestDetail, PurchaseQuotationRequestList, PurchaseQuotationRequestDetail,
    PurchaseRequestListForPQR, PurchaseQuotationList, PurchaseQuotationDetail, PurchaseQuotationRequestListForPQ
)

# purchase request
urlpatterns = [
    path('purchase-request/list', PurchaseRequestList.as_view(), name='PurchaseRequestList'),
    path('purchase-request-for-pqr/list', PurchaseRequestListForPQR.as_view(), name='PurchaseRequestListForPQR'),
    path('purchase-request/<str:pk>', PurchaseRequestDetail.as_view(), name='PurchaseRequestDetail'),
] + [
    path(
        'purchase-quotation-request/list',
        PurchaseQuotationRequestList.as_view(),
        name='PurchaseQuotationRequestList'
    ),
    path(
        'purchase-quotation-request-for-pq/list',
        PurchaseQuotationRequestListForPQ.as_view(),
        name='PurchaseQuotationRequestListForPQ'
    ),
    path(
        'purchase-quotation-request/<str:pk>',
        PurchaseQuotationRequestDetail.as_view(),
        name='PurchaseQuotationRequestDetail'
    ),
] + [
    path(
        'purchase-quotation/list',
        PurchaseQuotationList.as_view(),
        name='PurchaseQuotationList'
    ),
    path(
        'purchase-quotation/<str:pk>',
        PurchaseQuotationDetail.as_view(),
        name='PurchaseQuotationDetail'
    ),
]
