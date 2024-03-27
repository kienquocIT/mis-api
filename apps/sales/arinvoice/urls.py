from django.urls import path
from apps.sales.arinvoice.views import (
    DeliveryListForARInvoice, ARInvoiceList, ARInvoiceDetail, ARInvoiceSignList
)

urlpatterns = [
    path('list', ARInvoiceList.as_view(), name='ARInvoiceList'),
    path('detail/<str:pk>', ARInvoiceDetail.as_view(), name='ARInvoiceDetail'),
    path('get-deliveries', DeliveryListForARInvoice.as_view(), name='DeliveryListForARInvoice'),
    path('sign/list', ARInvoiceSignList.as_view(), name='ARInvoiceSignList'),
]
