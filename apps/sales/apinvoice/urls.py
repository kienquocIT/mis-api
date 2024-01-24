from django.urls import path
from apps.sales.apinvoice.views import (
    GoodsReceiptListForAPInvoice, APInvoiceList, APInvoiceDetail
)

urlpatterns = [
    path('list', APInvoiceList.as_view(), name='APInvoiceList'),
    path('detail/<str:pk>', APInvoiceDetail.as_view(), name='APInvoiceDetail'),
    path('get-goods-receipts', GoodsReceiptListForAPInvoice.as_view(), name='GoodsReceiptListForAPInvoice'),
]
