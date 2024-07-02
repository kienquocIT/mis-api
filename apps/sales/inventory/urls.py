from django.urls import path

from apps.sales.inventory.views import (
    GoodsReceiptList, GoodsReceiptDetail, GoodsTransferList, GoodsTransferDetail,
    InventoryAdjustmentList, InventoryAdjustmentDetail, InventoryAdjustmentOtherList, GoodsIssueList,
    GoodsIssueDetail, InventoryAdjustmentProductList, SaleOrderListForGoodsReturn, DeliveryListForGoodsReturn,
    GoodsReturnList, GoodsReturnDetail, GoodsDetailList, GoodsDetailDataList,
    GoodsRegistrationList, GoodsRegistrationDetail,
    GoodsRegistrationProductWarehouseList,
    GoodsRegistrationProductWarehouseLotList,
    GoodsRegistrationProductWarehouseSerialList
)

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
        name='DeliveryListForGoodsReturn'
    ),
]

# goods detail
urlpatterns += [
    path('goods-detail/list', GoodsDetailList.as_view(), name='GoodsDetailList'),
    path('update-detail-data/list', GoodsDetailDataList.as_view(), name='GoodsDetailDataList'),
]

# goods registration
urlpatterns += [
    path('goods-registration/list', GoodsRegistrationList.as_view(), name='GoodsRegistrationList'),
    path('goods-registration/<str:pk>', GoodsRegistrationDetail.as_view(), name='GoodsRegistrationDetail'),
    path(
        'goods-registration-prd-wh',
        GoodsRegistrationProductWarehouseList.as_view(),
        name='GoodsRegistrationProductWarehouseList'
    ),
    path(
        'goods-registration-prd-wh-lot',
        GoodsRegistrationProductWarehouseLotList.as_view(),
        name='GoodsRegistrationProductWarehouseLotList'
    ),
    path(
        'goods-registration-prd-wh-serial',
        GoodsRegistrationProductWarehouseSerialList.as_view(),
        name='GoodsRegistrationProductWarehouseSerialList'
    ),
]
