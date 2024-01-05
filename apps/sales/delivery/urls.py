from django.urls import path

from apps.sales.delivery.views import (
    DeliveryConfigDetail, SaleOrderActiveDelivery,
    OrderPickingSubList, OrderPickingSubDetail, OrderDeliverySubList, OrderDeliverySubDetail
)

urlpatterns = [
    path('config', DeliveryConfigDetail.as_view(), name='DeliveryConfigDetail'),
    path('sale-order/<str:pk>', SaleOrderActiveDelivery.as_view(), name='SaleOrderActiveDelivery'),  # pk = SaleOrder

    path('picking', OrderPickingSubList.as_view(), name='OrderPickingList'),
    path('picking/<str:pk>', OrderPickingSubDetail.as_view(), name='OrderPickingSubDetail'),
    path('', OrderDeliverySubList.as_view(), name='OrderDeliveryList'),
    path('sub/<str:pk>', OrderDeliverySubDetail.as_view(), name='OrderDeliverySubDetail'),
]
