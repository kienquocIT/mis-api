from django.urls import path

from .views import AssetToolConfigDetail, AssetToolsProvideRequestList, AssetToolsProvideRequestDetail, \
    AssetToolsDeliveryRequestList, AssetToolsProductUsedList

urlpatterns = [
    # CONFIG
    path('config', AssetToolConfigDetail.as_view(), name='AssetToolConfigDetail'),
    # PROVIDE
    path('provide', AssetToolsProvideRequestList.as_view(), name='AssetToolsProvideRequestList'),
    path('provide/detail/<str:pk>', AssetToolsProvideRequestDetail.as_view(), name='AssetToolsProvideRequestDetail'),
    # DELIVERY
    path('delivery', AssetToolsDeliveryRequestList.as_view(), name='AssetToolsDeliveryRequestList'),
    path('delivery/product-view-list', AssetToolsProductUsedList.as_view(), name='AssetToolsProductUsedList'),

]
