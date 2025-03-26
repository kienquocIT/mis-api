from django.urls import path

from .views import (
    LeaseOrderList, LeaseOrderDetail, LORecurrenceList, LeaseOrderConfigDetail,
)

urlpatterns = [
    path('config', LeaseOrderConfigDetail.as_view(), name='LeaseOrderConfigDetail'),
    path('list', LeaseOrderList.as_view(), name='LeaseOrderList'),
    path('<str:pk>', LeaseOrderDetail.as_view(), name='LeaseOrderDetail'),

    path('lease-order-recurrence/list', LORecurrenceList.as_view(), name='LORecurrenceList'),
]
