from django.urls import path

from apps.sales.inventory.views import GoodsTransferList, GoodsTransferDetail, GoodsReceiptList, GoodsReceiptDetail, \
    GoodsIssueList, GoodsIssueDetail
from apps.sales.inventory.views.inventory_adjustment import InventoryAdjustmentList, InventoryAdjustmentDetail, \
    InventoryAdjustmentProductList

urlpatterns = [
    # goods receipt
    path('goods-receipt/list', GoodsReceiptList.as_view(), name='GoodsReceiptList'),
    path('goods-receipt/<str:pk>', GoodsReceiptDetail.as_view(), name='GoodsReceiptDetail'),
    # inventory adjustment
    path('inventory-adjustments', InventoryAdjustmentList.as_view(), name='InventoryAdjustmentList'),
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
    path('goods-transfer/<str:pk>', GoodsTransferDetail.as_view(), name='GoodsTransferList'),
]

# goods issue
urlpatterns += [
    path('goods-issue/list', GoodsIssueList.as_view(), name='GoodsIssueList'),
    path('goods-issue/<str:pk>', GoodsIssueDetail.as_view(), name='GoodsIssueDetail'),
]
