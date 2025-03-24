from django.urls import path

from .views import GroupOrderProductList, GroupOrderProductPriceListList

urlpatterns = [
    path('product/list', GroupOrderProductList.as_view(), name='GroupOrderProductList'),
    path(
        'product-price-list/list',
        GroupOrderProductPriceListList.as_view(),
        name='GroupOrderProductPriceListList'
    ),
]
