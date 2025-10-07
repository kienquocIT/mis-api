from django.urls import path
from apps.sales.serviceorder.views import (
    ServiceOrderList, ServiceOrderDetail, ServiceOrderDetailDashboard, SVODeliveryWorkOrderDetail,
)

urlpatterns = [
    path('list', ServiceOrderList.as_view(), name='ServiceOrderList'),
    path('detail/<str:pk>', ServiceOrderDetail.as_view(), name='ServiceOrderDetail'),
    path('detail-dashboard/<str:pk>', ServiceOrderDetailDashboard.as_view(), name='ServiceOrderDetailDashboard'),
    path('work-order-detail', SVODeliveryWorkOrderDetail.as_view(), name='SVODeliveryWorkOrderDetail')
]
