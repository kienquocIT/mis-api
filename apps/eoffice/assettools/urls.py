from django.urls import path

from .views import AssetToolConfigDetail, AssetToolsProvideRequestList

urlpatterns = [
    path('config', AssetToolConfigDetail.as_view(), name='AssetToolConfigDetail'),
    path('provide', AssetToolsProvideRequestList.as_view(), name='AssetToolsProvideRequestList'),
]
