from django.urls import path

from apps.sales.fixedasset.views import FixedAssetList

urlpatterns = [
    path('list', FixedAssetList.as_view(), name='FixedAssetList'),
]
