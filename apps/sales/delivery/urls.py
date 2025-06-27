from django.urls import path

from apps.sales.delivery.views import (
    DeliveryConfigDetail, SaleOrderActiveDelivery,
    OrderPickingSubList, OrderPickingSubDetail, OrderDeliverySubList, OrderDeliverySubDetail,
    LeaseOrderActiveDelivery, OrderDeliverySubRecoveryList
)
from apps.sales.delivery.views.delivery import DeliveryProductLeaseList

urlpatterns = [
    path('config', DeliveryConfigDetail.as_view(), name='DeliveryConfigDetail'),
    path('sale-order/<str:pk>', SaleOrderActiveDelivery.as_view(), name='SaleOrderActiveDelivery'),  # SaleOrder
    path('lease-order/<str:pk>', LeaseOrderActiveDelivery.as_view(), name='LeaseOrderActiveDelivery'),  # LeaseOrder

    path('picking', OrderPickingSubList.as_view(), name='OrderPickingList'),
    path('picking/<str:pk>', OrderPickingSubDetail.as_view(), name='OrderPickingSubDetail'),
    path('', OrderDeliverySubList.as_view(), name='OrderDeliveryList'),
    path('sub/<str:pk>', OrderDeliverySubDetail.as_view(), name='OrderDeliverySubDetail'),

    path('for-recovery', OrderDeliverySubRecoveryList.as_view(), name='OrderDeliverySubRecoveryList'),
    path('product-lease', DeliveryProductLeaseList.as_view(), name='DeliveryProductLeaseList'),
]
