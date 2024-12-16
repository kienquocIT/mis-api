from django.urls import path

from .views import (
    LeaseOrderList, LeaseOrderDetail,
)

urlpatterns = [
    path('list', LeaseOrderList.as_view(), name='LeaseOrderList'),
    path('<str:pk>', LeaseOrderDetail.as_view(), name='LeaseOrderDetail'),
]
