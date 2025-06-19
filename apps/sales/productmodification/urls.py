from django.urls import path
from apps.sales.productmodification.views import (
    WarehouseListByProduct, ProductSerialList, ProductModifiedList, ProductComponentList, ProductModificationList,
    ProductModificationDetail, ProductLotList, ProductModificationDDList, ProductModificationProductGRList,
    ProductModifiedBeforeList, LatestComponentList
)

urlpatterns = [
    path('list', ProductModificationList.as_view(), name='ProductModificationList'),
    path('detail/<str:pk>', ProductModificationDetail.as_view(), name='ProductModificationDetail'),
    path('product-modified-list', ProductModifiedList.as_view(), name='ProductModifiedList'),
    path('product-modified-before-list', ProductModifiedBeforeList.as_view(), name='ProductModifiedBeforeList'),
    path('product-component-list', ProductComponentList.as_view(), name='ProductComponentList'),
    path('latest-component-list', LatestComponentList.as_view(), name='LatestComponentList'),
    path('warehouse-list-by-product', WarehouseListByProduct.as_view(), name='WarehouseListByProduct'),
    path('product-lot-list', ProductLotList.as_view(), name='ProductLotList'),
    path('product-serial-list', ProductSerialList.as_view(), name='ProductSerialList'),
    path('dropdown/list', ProductModificationDDList.as_view(), name='ProductModificationDDList'),
    path(
        'product-modification-product-gr/list',
        ProductModificationProductGRList.as_view(),
        name='ProductModificationProductGRList'
    )
]
