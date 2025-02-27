from django.urls import path

from apps.sales.inventory.views import (
    GoodsReceiptList, GoodsReceiptDetail, GoodsTransferList, GoodsTransferDetail,
    InventoryAdjustmentList, InventoryAdjustmentDetail, InventoryAdjustmentGRList, GoodsIssueList,
    GoodsIssueDetail, InventoryAdjustmentProductList, SaleOrderListForGoodsReturn, DeliveryListForGoodsReturn,
    GoodsReturnList, GoodsReturnDetail, GoodsDetailList, GoodsDetailDataList,
    GoodsRegistrationList,
    GoodsRegistrationDetail,
    GReItemProductWarehouseLotList,
    GReItemProductWarehouseSerialList,
    GReItemProductWarehouseList,
    ProjectProductList, GReItemBorrowList, GReItemBorrowDetail,
    GReItemSubList, GoodsRegistrationItemAvailableQuantity, GoodsRegisBorrowList, NoneGReItemBorrowList,
    NoneGReItemBorrowDetail, NoneGoodsRegistrationItemAvailableQuantity, ProductionOrderListForGIS,
    ProductionOrderDetailForGIS, InventoryAdjustmentListForGIS, InventoryAdjustmentDetailForGIS,
    ProductWareHouseSerialListForGIS, ProductWareHouseLotListForGIS, ProductWareHouseListForGIS, WorkOrderListForGIS,
    WorkOrderDetailForGIS, GoodsIssueProductList, GoodsDetailListImportDB, GoodsDetailSerialDataList, GoodsRecoveryList,
    GoodsRecoveryDetail, GoodsRecoveryLeaseGenerateList,
)

urlpatterns = [
    # goods receipt
    path('goods-receipt/list', GoodsReceiptList.as_view(), name='GoodsReceiptList'),
    path('goods-receipt/<str:pk>', GoodsReceiptDetail.as_view(), name='GoodsReceiptDetail'),
    # goods recovery
    path('goods-recovery/list', GoodsRecoveryList.as_view(), name='GoodsRecoveryList'),
    path('goods-recovery/<str:pk>', GoodsRecoveryDetail.as_view(), name='GoodsRecoveryDetail'),
    path(
        'goods-recovery-lease-generate/list',
        GoodsRecoveryLeaseGenerateList.as_view(),
        name='GoodsRecoveryLeaseGenerateList'
    ),

    # inventory adjustment
    path('inventory-adjustments', InventoryAdjustmentList.as_view(), name='InventoryAdjustmentList'),
    path(
        'inventory-adjustments-gr',
        InventoryAdjustmentGRList.as_view(),
        name='InventoryAdjustmentGRList'
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
    path('goods-issue-product/list', GoodsIssueProductList.as_view(), name='GoodsIssueProductList'),
    # Inventory Adjustment for GIS
    path(
        'inventory-adjustment-for-gis/list',
        InventoryAdjustmentListForGIS.as_view(),
        name='InventoryAdjustmentListForGIS'
    ),
    path(
        'inventory-adjustment-for-gis/<str:pk>',
        InventoryAdjustmentDetailForGIS.as_view(),
        name='InventoryAdjustmentDetailForGIS'
    ),
    # Production order for GIS
    path(
        'production-order-for-gis/list',
        ProductionOrderListForGIS.as_view(),
        name='ProductionOrderListForGIS'
    ),
    path(
        'production-order-for-gis/<str:pk>',
        ProductionOrderDetailForGIS.as_view(),
        name='ProductionOrderDetailForGIS'
    ),
    path(
        'work-order-for-gis/list',
        WorkOrderListForGIS.as_view(),
        name='WorkOrderListForGIS'
    ),
    path(
        'work-order-for-gis/<str:pk>',
        WorkOrderDetailForGIS.as_view(),
        name='WorkOrderDetailForGIS'
    ),
    path(
        'prd-wh-list-for-gis/list',
        ProductWareHouseListForGIS.as_view(),
        name='ProductWareHouseListForGIS'
    ),
    path(
        'lot-list-for-gis/list',
        ProductWareHouseLotListForGIS.as_view(),
        name='ProductWareHouseLotListForGIS'
    ),
    path(
        'serial-list-for-gis/list',
        ProductWareHouseSerialListForGIS.as_view(),
        name='ProductWareHouseSerialListForGIS'
    ),
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
    path('goods-detail-sn-data/list', GoodsDetailSerialDataList.as_view(), name='GoodsDetailSerialDataList'),
    path('create-update-goods-detail-data/list', GoodsDetailDataList.as_view(), name='GoodsDetailDataList'),
    path(
        'goods-detail-import-db',
        GoodsDetailListImportDB.as_view(),
        name='GoodsDetailListImportDB'
    ),
]

# goods registration
urlpatterns += [
    path('goods-registration/list', GoodsRegistrationList.as_view(), name='GoodsRegistrationList'),
    path('goods-registration/<str:pk>', GoodsRegistrationDetail.as_view(), name='GoodsRegistrationDetail'),
    path('gre-item-sub/list', GReItemSubList.as_view(), name='GReItemSubList'),
    path('gre-item-prd-wh', GReItemProductWarehouseList.as_view(), name='GReItemProductWarehouseList'),
    path('gre-item-prd-wh-lot', GReItemProductWarehouseLotList.as_view(), name='GReItemProductWarehouseLotList'),
    path(
        'gre-item-prd-wh-serial', GReItemProductWarehouseSerialList.as_view(), name='GReItemProductWarehouseSerialList'
    ),
    path('product-list-for-project', ProjectProductList.as_view(), name='ProjectProductList'),
    path('gre-item-borrow/list', GReItemBorrowList.as_view(), name='GReItemBorrowList'),
    path('gre-item-borrow/<str:pk>', GReItemBorrowDetail.as_view(), name='GReItemBorrowDetail'),
    path(
        'gre-item-available-quantity',
        GoodsRegistrationItemAvailableQuantity.as_view(),
        name='GoodsRegistrationItemAvailableQuantity'
    ),
    path('none-gre-item-borrow/list', NoneGReItemBorrowList.as_view(), name='NoneGReItemBorrowList'),
    path('none-gre-item-borrow/<str:pk>', NoneGReItemBorrowDetail.as_view(), name='NoneGReItemBorrowDetail'),
    path(
        'none-gre-item-available-quantity',
        NoneGoodsRegistrationItemAvailableQuantity.as_view(),
        name='NoneGoodsRegistrationItemAvailableQuantity'
    ),
    path('goods-regis-borrow/list', GoodsRegisBorrowList.as_view(), name='GoodsRegisBorrowList'),
]
