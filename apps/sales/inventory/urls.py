from django.urls import path

from apps.sales.inventory.views import GoodsTransferList, GoodsTransferDetail
from apps.sales.inventory.views import GoodsReceiptList, GoodsReceiptDetail
from apps.sales.inventory.views.inventory_adjustment import InventoryAdjustmentList, InventoryAdjustmentDetail

urlpatterns = [
    # good receipt
    path('goods-receipt/list', GoodsReceiptList.as_view(), name='GoodsReceiptList'),
    path('goods-receipt/<str:pk>', GoodsReceiptDetail.as_view(), name='GoodsReceiptDetail'),
    # inventory adjustment
    path('inventory-adjustments', InventoryAdjustmentList.as_view(), name='InventoryAdjustmentList'),
    path('inventory-adjustment/<str:pk>', InventoryAdjustmentDetail.as_view(), name='InventoryAdjustmentDetail'),
]

# good transfer
urlpatterns += [
    path('good-transfer/list', GoodsTransferList.as_view(), name='GoodsTransferList'),
    path('good-transfer/<str:pk>', GoodsTransferDetail.as_view(), name='GoodsTransferList'),
]
