from django.urls import path
from apps.sales.productmodificationbom.views import (
    PMBOMProductModifiedList, PMBOMProductComponentList, ProductModificationBOMList,
    ProductModificationBOMDetail, PMBOMProductModifiedBeforeList, PMBOMLatestComponentList
)

urlpatterns = [
    path('list', ProductModificationBOMList.as_view(), name='ProductModificationBOMList'),
    path('detail/<str:pk>', ProductModificationBOMDetail.as_view(), name='ProductModificationBOMDetail'),
    path('product-modified-list', PMBOMProductModifiedList.as_view(), name='PMBOMProductModifiedList'),
    path(
        'product-modified-before-list',
        PMBOMProductModifiedBeforeList.as_view(),
        name='PMBOMProductModifiedBeforeList'
    ),
    path('product-component-list', PMBOMProductComponentList.as_view(), name='PMBOMProductComponentList'),
    path('latest-component-list', PMBOMLatestComponentList.as_view(), name='PMBOMLatestComponentList'),
]
