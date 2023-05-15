from django.urls import path

from .views import SaleOrderList, SaleOrderDetail

urlpatterns = [
    path('lists', SaleOrderList.as_view(), name='SaleOrderList'),
    path('<str:pk>', SaleOrderDetail.as_view(), name='SaleOrderDetail'),
]
