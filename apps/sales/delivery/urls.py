from django.urls import path

from apps.sales.delivery.views import (
    DeliveryConfigDetail, SaleOrderActiveDelivery,
    OrderPickingSubList, OrderPickingSubDetail, OrderDeliverySubList, OrderDeliverySubDetail,
    LeaseOrderActiveDelivery, OrderDeliverySubRecoveryList, DeliveryProductLeaseList, OrderDeliverySubDetailPrint,
    DeliveryWorkLogList
)
from apps.sales.delivery.views.config import ServiceOrderActiveDelivery

urlpatterns = [
    path('config', DeliveryConfigDetail.as_view(), name='DeliveryConfigDetail'),
    path('sale-order/<str:pk>', SaleOrderActiveDelivery.as_view(), name='SaleOrderActiveDelivery'),
    path('lease-order/<str:pk>', LeaseOrderActiveDelivery.as_view(), name='LeaseOrderActiveDelivery'),
    path('service-order/<str:pk>', ServiceOrderActiveDelivery.as_view(), name='ServiceOrderActiveDelivery'),

    path('picking', OrderPickingSubList.as_view(), name='OrderPickingList'),
    path('picking/<str:pk>', OrderPickingSubDetail.as_view(), name='OrderPickingSubDetail'),
    path('', OrderDeliverySubList.as_view(), name='OrderDeliveryList'),
    path('sub/<str:pk>', OrderDeliverySubDetail.as_view(), name='OrderDeliverySubDetail'),
    path('sub-print/<str:pk>', OrderDeliverySubDetailPrint.as_view(), name='OrderDeliverySubDetailPrint'),

    path('for-recovery', OrderDeliverySubRecoveryList.as_view(), name='OrderDeliverySubRecoveryList'),
    path('product-lease', DeliveryProductLeaseList.as_view(), name='DeliveryProductLeaseList'),
    path('work-log', DeliveryWorkLogList.as_view(), name='DeliveryWorkLogList'),
]
