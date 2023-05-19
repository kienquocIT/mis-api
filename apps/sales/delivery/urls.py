from django.urls import path

from apps.sales.delivery.views import (
    DeliveryConfigDetail, SaleOrderActiveDelivery,
    OrderPickingList, OrderPickingDetail,
)

urlpatterns = [
    path('config', DeliveryConfigDetail.as_view(), name='DeliveryConfigDetail'),
    path('sale-order/<str:pk>', SaleOrderActiveDelivery.as_view(), name='SaleOrderActiveDelivery'),  # pk = SaleOrder

    path('picking', OrderPickingList.as_view(), name='OrderPickingList'),
    path('picking/<str:pk>', OrderPickingDetail.as_view(), name='OrderPickingDetail'),
]
