from django.urls import path

from apps.sales.asset.views import FixedAssetList, FixedAssetDetail, InstrumentToolList, InstrumentToolDetail, \
    FixedAssetWriteOffList

fixed_asset_urlpatterns = [
    path('fixed-asset/list', FixedAssetList.as_view(), name='FixedAssetList'),
    path('fixed-asset/detail/<str:pk>', FixedAssetDetail.as_view(), name='FixedAssetDetail'),
]

instrument_tool_urlpatterns = [
    path('instrument-tool/list', InstrumentToolList.as_view(), name='InstrumentToolList'),
    path('instrument-tool/detail/<str:pk>', InstrumentToolDetail.as_view(), name='InstrumentToolDetail'),
]

fixed_asset_write_off_urlpatterns = [
    path('fixed-asset-write-off/list', FixedAssetWriteOffList.as_view(), name='FixedAssetWriteOffList'),
]
urlpatterns = fixed_asset_urlpatterns + instrument_tool_urlpatterns + fixed_asset_write_off_urlpatterns
