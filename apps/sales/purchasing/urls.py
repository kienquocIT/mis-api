from django.urls import path

from apps.sales.purchasing.views import (
    PurchaseRequestList, PurchaseRequestDetail, PurchaseQuotationRequestList, PurchaseQuotationRequestDetail,
    PurchaseRequestListForPQR, PurchaseRequestProductList, PurchaseOrderDetail, PurchaseOrderList,
    PurchaseQuotationRequestListForPQ, PurchaseQuotationList, PurchaseQuotationDetail, PurchaseQuotationProductList,
    PurchaseOrderProductGRList, PurchaseOrderSaleList, PurchaseRequestConfigDetail, PurchaseRequestSaleList,
    PurchaseQuotationSaleList, PurchaseOrderDDList, SaleOrderListForPR, SaleOrderProductListForPR,
    DistributionPlanProductListForPR, DistributionPlanListForPR, ServiceOrderListForPR, ServiceOrderProductListForPR
)

urlpatterns = [
    # purchase request
    path('purchase-request/config', PurchaseRequestConfigDetail.as_view(), name='PurchaseRequestConfigDetail'),
    path('purchase-request/list', PurchaseRequestList.as_view(), name='PurchaseRequestList'),
    path('purchase-request/list-sale', PurchaseRequestSaleList.as_view(), name='PurchaseRequestSaleList'),
    path('purchase-request/<str:pk>', PurchaseRequestDetail.as_view(), name='PurchaseRequestDetail'),
    path('pr-product/list', PurchaseRequestProductList.as_view(), name='PurchaseRequestProductList'),
    path('pr-so-list', SaleOrderListForPR.as_view(), name='SaleOrderListForPR'),
    path(
        'pr-so-product-list/<str:pk>',
        SaleOrderProductListForPR.as_view(),
        name='SaleOrderProductListForPR'
    ),
    path('pr-dp-list', DistributionPlanListForPR.as_view(), name='DistributionPlanListForPR'),
    path(
        'pr-dp-product-list/<str:pk>',
        DistributionPlanProductListForPR.as_view(),
        name='DistributionPlanProductListForPR'
    ),
    path('pr-svo-list', ServiceOrderListForPR.as_view(), name='ServiceOrderListForPR'),
    path(
        'pr-svo-product-list/<str:pk>',
        ServiceOrderProductListForPR.as_view(),
        name='ServiceOrderProductListForPR'
    ),

    # purchase quotation request
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
    path(
        'purchase-quotation-request-for-pq/list',
        PurchaseQuotationRequestListForPQ.as_view(),
        name='PurchaseQuotationRequestListForPQ'
    ),
    path('purchase-request-for-pqr/list', PurchaseRequestListForPQR.as_view(), name='PurchaseRequestListForPQR'),

    # purchase order
    path('purchase-order/list', PurchaseOrderList.as_view(), name='PurchaseOrderList'),
    path('purchase-order/list-sale', PurchaseOrderSaleList.as_view(), name='PurchaseOrderSaleList'),
    path('purchase-order/<str:pk>', PurchaseOrderDetail.as_view(), name='PurchaseOrderDetail'),
    path('purchase-order-product-gr/list', PurchaseOrderProductGRList.as_view(), name='PurchaseOrderProductGRList'),
    path('purchase-order-dropdown/list', PurchaseOrderDDList.as_view(), name='PurchaseOrderDDList'),

    # purchase quotation
    path('purchase-quotation/list', PurchaseQuotationList.as_view(), name='PurchaseQuotationList'),
    path('purchase-quotation/list-sale', PurchaseQuotationSaleList.as_view(), name='PurchaseQuotationSaleList'),
    path('purchase-quotation/<str:pk>', PurchaseQuotationDetail.as_view(), name='PurchaseQuotationDetail'),
    path(
        'purchase-quotation-product/list',
        PurchaseQuotationProductList.as_view(),
        name='PurchaseQuotationProductList'
    ),
]
