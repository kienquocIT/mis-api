from django.urls import path
from apps.sales.arinvoice.views import (
    DeliveryListForARInvoice, ARInvoiceList, ARInvoiceDetail, ARInvoiceSignList, ARInvoiceRecurrenceList,
    SaleOrderListForARInvoice
)

urlpatterns = [
    path('list', ARInvoiceList.as_view(), name='ARInvoiceList'),
    path('detail/<str:pk>', ARInvoiceDetail.as_view(), name='ARInvoiceDetail'),
    path('get-sale-order', SaleOrderListForARInvoice.as_view(), name='SaleOrderListForARInvoice'),
    path('get-deliveries', DeliveryListForARInvoice.as_view(), name='DeliveryListForARInvoice'),
    path('sign/list', ARInvoiceSignList.as_view(), name='ARInvoiceSignList'),
    path('recurrence/list', ARInvoiceRecurrenceList.as_view(), name='ARInvoiceRecurrenceList'),
]
