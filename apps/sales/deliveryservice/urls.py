from django.urls import path

from apps.sales.delivery.views import (
    DeliveryConfigDetail, SaleOrderActiveDelivery,
    OrderPickingSubList, OrderPickingSubDetail, OrderDeliverySubList, OrderDeliverySubDetail,
    LeaseOrderActiveDelivery, OrderDeliverySubRecoveryList
)
from apps.sales.delivery.views.delivery import DeliveryProductLeaseList

urlpatterns = [

]
