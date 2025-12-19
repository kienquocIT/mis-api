from django.urls import path

from apps.sales.asset.views import FixedAssetList, FixedAssetDetail, InstrumentToolList, InstrumentToolDetail, \
    FixedAssetWriteOffList, FixedAssetWriteOffDetail, InstrumentToolWriteOffList, InstrumentToolWriteOffDetail, \
    AssetForLeaseList, ToolForLeaseList, AssetStatusLeaseList, ToolStatusLeaseList, AssetListNoPerm, \
    InstrumentToolNoPermList, ProductWarehouseListForFixedAsset, FixedAssetListWithDepreciationList, \
    RunDepreciationAPIView

fixed_asset_urlpatterns = [
    path('fixed-asset/list', FixedAssetList.as_view(), name='FixedAssetList'),
    path('fixed-asset/detail/<str:pk>', FixedAssetDetail.as_view(), name='FixedAssetDetail'),
    path('fixed-asset-for-lease/list', AssetForLeaseList.as_view(), name='AssetForLeaseList'),
    path('fixed-asset-status-lease/list', AssetStatusLeaseList.as_view(), name='AssetStatusLeaseList'),
    path('fixed-asset/no-perm-list', AssetListNoPerm.as_view(), name='AssetListNoPerm'),
    path('fixed-asset/product-warehouse/list', ProductWarehouseListForFixedAsset.as_view(),
         name='ProductWarehouseListForFixedAsset'),
    path('fa-depreciation/list', FixedAssetListWithDepreciationList.as_view(),
         name='FixedAssetListWithDepreciationList'),
    path('run-depreciation', RunDepreciationAPIView.as_view(), name='RunDepreciationAPIView'),
]

instrument_tool_urlpatterns = [
    path('instrument-tool/list', InstrumentToolList.as_view(), name='InstrumentToolList'),
    path('instrument-tool/detail/<str:pk>', InstrumentToolDetail.as_view(), name='InstrumentToolDetail'),
    path('instrument-tool-for-lease/list', ToolForLeaseList.as_view(), name='ToolForLeaseList'),
    path('instrument-tool-status-lease/list', ToolStatusLeaseList.as_view(), name='ToolStatusLeaseList'),
    path('instrument-tool/no-perm-list', InstrumentToolNoPermList.as_view(), name='InstrumentToolNoPermList'),
]

fixed_asset_write_off_urlpatterns = [
    path('fixed-asset-writeoff/list', FixedAssetWriteOffList.as_view(), name='FixedAssetWriteOffList'),
    path(
        'fixed-asset-writeoff/detail/<str:pk>',
         FixedAssetWriteOffDetail.as_view(),
         name='FixedAssetWriteOffDetail'
    ),
]

instrument_tool_write_off_urlpatterns = [
    path('instrument-tool-writeoff/list', InstrumentToolWriteOffList.as_view(), name='InstrumentToolWriteOffList'),
    path(
        'instrument-tool-writeoff/detail/<str:pk>',
         InstrumentToolWriteOffDetail.as_view(),
         name='InstrumentToolWriteOffDetail'
    ),
]

urlpatterns = (
    fixed_asset_urlpatterns
    + instrument_tool_urlpatterns
    + fixed_asset_write_off_urlpatterns
    + instrument_tool_write_off_urlpatterns
)
