from django.urls import path
from apps.sales.serviceorder.views import (
    ServiceOrderList, ServiceOrderDetail, ServiceOrderDetailDashboard, SVODeliveryWorkOrderDetail,
    ServiceOrderDiff,
)

urlpatterns = [
    path('list', ServiceOrderList.as_view(), name='ServiceOrderList'),
    path('detail/<str:pk>', ServiceOrderDetail.as_view(), name='ServiceOrderDetail'),
    path('detail-dashboard/<str:pk>', ServiceOrderDetailDashboard.as_view(), name='ServiceOrderDetailDashboard'),
    path('diff/<str:current_id>/<str:comparing_id>', ServiceOrderDiff.as_view(), name='ServiceOrderDiff'),
    path('work-order-detail', SVODeliveryWorkOrderDetail.as_view(), name='SVODeliveryWorkOrderDetail')
]
