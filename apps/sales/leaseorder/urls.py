from django.urls import path

from .views import (
    LeaseOrderList, LeaseOrderDetail, LORecurrenceList, LeaseOrderConfigDetail, LeaseOrderDDList, LeaseOrderCostList,
)

urlpatterns = [
    path('config', LeaseOrderConfigDetail.as_view(), name='LeaseOrderConfigDetail'),
    path('list', LeaseOrderList.as_view(), name='LeaseOrderList'),
    path('<str:pk>', LeaseOrderDetail.as_view(), name='LeaseOrderDetail'),

    path('lease-order-recurrence/list', LORecurrenceList.as_view(), name='LORecurrenceList'),
    path('dropdown/list', LeaseOrderDDList.as_view(), name='LeaseOrderDDList'),
    path('cost/list', LeaseOrderCostList.as_view(), name='LeaseOrderCostList'),
]
