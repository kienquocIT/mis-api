from django.urls import path

from apps.sales.purchasing.views import (
    PurchaseRequestList, PurchaseRequestDetail, PurchaseQuotationRequestList, PurchaseQuotationRequestDetail,
    PurchaseRequestListForPQR, PurchaseRequestProductList, PurchaseOrderDetail, PurchaseOrderList,
    PurchaseQuotationRequestListForPQ, PurchaseQuotationList, PurchaseQuotationDetail, PurchaseQuotationProductList
)

urlpatterns = [
    # purchase request
    path('purchase-request/list', PurchaseRequestList.as_view(), name='PurchaseRequestList'),
    path('purchase-request-for-pqr/list', PurchaseRequestListForPQR.as_view(), name='PurchaseRequestListForPQR'),
    path('purchase-request/<str:pk>', PurchaseRequestDetail.as_view(), name='PurchaseRequestDetail'),
    path('purchase-request-product/list', PurchaseRequestProductList.as_view(), name='PurchaseRequestProductList'),
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
    # purchase order
    path('purchase-order/list', PurchaseOrderList.as_view(), name='PurchaseOrderList'),
    path('purchase-order/<str:pk>', PurchaseOrderDetail.as_view(), name='PurchaseOrderDetail'),
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
    path(
        'purchase-quotation-product/list',
        PurchaseQuotationProductList.as_view(),
        name='PurchaseQuotationProductList'
    ),
]
