from django.urls import path

from apps.sales.delivery.views import (
    DeliveryConfigDetail, SaleOrderActiveDelivery,
    OrderPickingList, OrderPickingDetail, OrderDeliveryList, OrderDeliveryDetail, OrderDeliverySubDetail
)

urlpatterns = [
    path('config', DeliveryConfigDetail.as_view(), name='DeliveryConfigDetail'),
    path('sale-order/<str:pk>', SaleOrderActiveDelivery.as_view(), name='SaleOrderActiveDelivery'),  # pk = SaleOrder

    path('picking', OrderPickingList.as_view(), name='OrderPickingList'),
    path('picking/<str:pk>', OrderPickingDetail.as_view(), name='OrderPickingDetail'),
    path('', OrderDeliveryList.as_view(), name='OrderDeliveryList'),
    path('<str:pk>', OrderDeliveryDetail.as_view(), name='OrderDeliveryDetail'),
    path('sub/<str:pk>', OrderDeliverySubDetail.as_view(), name='OrderDeliverySubDetail'),
]
