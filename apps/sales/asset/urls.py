from django.urls import path

from apps.sales.asset.views import FixedAssetList, FixedAssetDetail

fixed_asset_urlpatterns = [
    path('fixed-asset/list', FixedAssetList.as_view(), name='FixedAssetList'),
    path('fixed-asset/detail/<str:pk>', FixedAssetDetail.as_view(), name='FixedAssetDetail'),
]

urlpatterns = fixed_asset_urlpatterns
