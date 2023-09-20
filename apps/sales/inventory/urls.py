from django.urls import path

from apps.sales.inventory.views import GoodsTransferList, GoodsTransferDetail
from apps.sales.inventory.views.goods_receipt import GoodsReceiptList, GoodsReceiptDetail

urlpatterns = [
    # good receipt
    path('goods-receipt/list', GoodsReceiptList.as_view(), name='GoodsReceiptList'),
    path('goods-receipt/<str:pk>', GoodsReceiptDetail.as_view(), name='GoodsReceiptDetail'),
]

# good transfer
urlpatterns += [
    path('good-transfer/list', GoodsTransferList.as_view(), name='GoodsTransferList'),
    path('good-transfer/<str:pk>', GoodsTransferDetail.as_view(), name='GoodsTransferList'),
]
