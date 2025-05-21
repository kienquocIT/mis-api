from django.urls import path
from apps.sales.productmodification.views import (
    WarehouseListByProduct, ProductSerialList, ProductModifiedList, ProductComponentList
)

urlpatterns = [
    path('product-modified-list', ProductModifiedList.as_view(), name='ProductModifiedList'),
    path('product-component-list', ProductComponentList.as_view(), name='ProductComponentList'),
    path('warehouse-list-by-product', WarehouseListByProduct.as_view(), name='WarehouseListByProduct'),
    path('product-serial-list', ProductSerialList.as_view(), name='ProductSerialList'),
]
