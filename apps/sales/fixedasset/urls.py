from django.urls import path

from apps.sales.fixedasset.views import FixedAssetList, FixedAssetDetail

urlpatterns = [
    path('list', FixedAssetList.as_view(), name='FixedAssetList'),
    path('detail/<str:pk>', FixedAssetDetail.as_view(), name='FixedAssetDetail'),
]
