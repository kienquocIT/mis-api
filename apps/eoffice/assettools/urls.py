from django.urls import path

from .views import AssetToolConfigDetail, AssetToolsProvideRequestList, AssetToolsProvideRequestDetail

urlpatterns = [
    path('config', AssetToolConfigDetail.as_view(), name='AssetToolConfigDetail'),
    path('provide', AssetToolsProvideRequestList.as_view(), name='AssetToolsProvideRequestList'),
    path('provide/detail/<str:pk>', AssetToolsProvideRequestDetail.as_view(), name='AssetToolsProvideRequestDetail'),
]
