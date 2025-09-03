from django.urls import path
from apps.sales.serviceorder.views import (
    ServiceOrderList, ServiceOrderDetail
)

urlpatterns = [
    path('list', ServiceOrderList.as_view(), name='ServiceOrderList'),
    path('detail/<str:pk>', ServiceOrderDetail.as_view(), name='ServiceOrderDetail'),
]
