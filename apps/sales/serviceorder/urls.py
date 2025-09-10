from django.urls import path
from apps.sales.serviceorder.views import (
    ServiceOrderList, ServiceOrderDetail, ServiceOrderDetailForDashboard
)

urlpatterns = [
    path('list', ServiceOrderList.as_view(), name='ServiceOrderList'),
    path('detail/<str:pk>', ServiceOrderDetail.as_view(), name='ServiceOrderDetail'),
    path(
        'detail-for-dashboard/<str:pk>',
        ServiceOrderDetailForDashboard.as_view(),
        name='ServiceOrderDetailForDashboard'
    ),
]
