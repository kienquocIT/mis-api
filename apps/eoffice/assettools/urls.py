from django.urls import path

from .views import AssetToolConfigDetail, AssetToolsProvideRequestList, AssetToolsProvideRequestDetail, \
    AssetToolsDeliveryRequestList, AssetToolsProductUsedList, AssetToolsProductListByProvideIDList, \
    AssetToolsDeliveryRequestDetail, AssetToolsReturnList, AssetToolsReturnDetail

urlpatterns = [
    # CONFIG
    path('config', AssetToolConfigDetail.as_view(), name='AssetToolConfigDetail'),
    # ASSET, TOOLS LIST
    path('list', AssetToolsProductUsedList.as_view(), name='AssetToolsProductUsedList'),
    # PROVIDE
    path('provide', AssetToolsProvideRequestList.as_view(), name='AssetToolsProvideRequestList'),
    path('provide/detail/<str:pk>', AssetToolsProvideRequestDetail.as_view(), name='AssetToolsProvideRequestDetail'),
    path(
        'provide/product-list-by-provide-id', AssetToolsProductListByProvideIDList.as_view(),
        name='AssetToolsProductListByProvideIDList'
    ),
    # DELIVERY
    path('delivery', AssetToolsDeliveryRequestList.as_view(), name='AssetToolsDeliveryRequestList'),
    path('delivery/detail/<str:pk>', AssetToolsDeliveryRequestDetail.as_view(), name='AssetToolsDeliveryRequestDetail'),
    # ASSET RETURN
    path('asset-return', AssetToolsReturnList.as_view(), name='AssetToolsReturnList'),
    path('asset-return/detail/<str:pk>', AssetToolsReturnDetail.as_view(), name='AssetToolsReturnDetail'),
]
