from django.urls import path

from apps.sales.inventory.views import GoodsReceiptList, GoodsReceiptDetail, GoodsTransferList, GoodsTransferDetail, \
    InventoryAdjustmentList, InventoryAdjustmentDetail, InventoryAdjustmentOtherList, GoodsIssueList, \
    GoodsIssueDetail, InventoryAdjustmentProductList, SaleOrderListForGoodsReturn, DeliveryListForGoodsReturn, \
    GetDeliveryProductsDetail, GoodsReturnList, GoodsReturnDetail, GoodsDetailList

urlpatterns = [
    # goods receipt
    path('goods-receipt/list', GoodsReceiptList.as_view(), name='GoodsReceiptList'),
    path('goods-receipt/<str:pk>', GoodsReceiptDetail.as_view(), name='GoodsReceiptDetail'),
    # inventory adjustment
    path('inventory-adjustments', InventoryAdjustmentList.as_view(), name='InventoryAdjustmentList'),
    path(
        'inventory-adjustments-other',
        InventoryAdjustmentOtherList.as_view(),
        name='InventoryAdjustmentOtherList'
    ),
    path('inventory-adjustment/<str:pk>', InventoryAdjustmentDetail.as_view(), name='InventoryAdjustmentDetail'),
    path(
        'inventory-adjustment/product/list/<str:inventory_adjustment_mapped_id>',
        InventoryAdjustmentProductList.as_view(),
        name='InventoryAdjustmentProductList'
    )
]

# goods transfer
urlpatterns += [
    path('goods-transfer/list', GoodsTransferList.as_view(), name='GoodsTransferList'),
    path('goods-transfer/<str:pk>', GoodsTransferDetail.as_view(), name='GoodsTransferDetail'),
]

# goods issue
urlpatterns += [
    path('goods-issue/list', GoodsIssueList.as_view(), name='GoodsIssueList'),
    path('goods-issue/<str:pk>', GoodsIssueDetail.as_view(), name='GoodsIssueDetail'),
]

# goods return
urlpatterns += [
    path('goods-return/list', GoodsReturnList.as_view(), name='GoodsReturnList'),
    path('goods-return/<str:pk>', GoodsReturnDetail.as_view(), name='GoodsReturnDetail'),
    path(
        'sale-orders-for-goods-return/list',
        SaleOrderListForGoodsReturn.as_view(),
        name='SaleOrderListForGoodsReturn'
    ),
    path(
        'get-deliveries-for-goods-return',
        DeliveryListForGoodsReturn.as_view(),
        name='DeliveryListForGoodsReturn'),
    path(
        'get-delivery-products-for-goods-return/<str:pk>',
        GetDeliveryProductsDetail.as_view(),
        name='GetDeliveryProductsDetail'),
]

# goods detail
urlpatterns += [
    path('goods-detail/list', GoodsDetailList.as_view(), name='GoodsDetailList'),
]
