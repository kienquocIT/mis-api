from django.urls import path

from apps.sales.inventory.views.goods_receipt import GoodsReceiptList, GoodsReceiptDetail

urlpatterns = [
    # good receipt
    path('goods-receipt/list', GoodsReceiptList.as_view(), name='GoodsReceiptList'),
    path('goods-receipt/<str:pk>', GoodsReceiptDetail.as_view(), name='GoodsReceiptDetail'),
]
