from django.urls import path

from .views import GroupOrderProductList, GroupOrderProductPriceListList, GroupOrderList, GroupOrderDetail

urlpatterns = [
    path('product/list', GroupOrderProductList.as_view(), name='GroupOrderProductList'),
    path(
        'product-price-list/list',
        GroupOrderProductPriceListList.as_view(),
        name='GroupOrderProductPriceListList'
    ),
    path( 'list', GroupOrderList.as_view(), name='GroupOrderList'),
    path('detail/<str:pk>', GroupOrderDetail.as_view(), name='GroupOrderDetail'),
]
