from django.urls import path
from apps.accounting.accountingsettings.views.account_masterdata_views import (
    ChartOfAccountsList, DefaultAccountDeterminationList, DefaultAccountDeterminationDetail
)
from apps.accounting.accountingsettings.views.dimension import DimensionDefinitionList, DimensionDefinitionDetail, \
    DimensionDefinitionWithValueList, DimensionValueList, DimensionValueDetail, DimensionSyncConfigApplicationList, \
    DimensionSyncConfigList
from apps.accounting.accountingsettings.views.prd_account_deter_views import ProductAccountDeterminationList, \
    ProductAccountDeterminationDetail
from apps.accounting.accountingsettings.views.prd_type_account_deter_views import ProductTypeAccountDeterminationList, \
    ProductTypeAccountDeterminationDetail
from apps.accounting.accountingsettings.views.wh_account_deter_views import WarehouseAccountDeterminationList, \
    WarehouseAccountDeterminationDetail

urlpatterns = [
    path('chart-of-accounts/list', ChartOfAccountsList.as_view(), name='ChartOfAccountsList'),
    path(
        'default-account-determination/list',
        DefaultAccountDeterminationList.as_view(),
        name='DefaultAccountDeterminationList'
    ),
    path(
        'default-account-determination/detail/<str:pk>',
        DefaultAccountDeterminationDetail.as_view(),
        name='DefaultAccountDeterminationDetail'
    ),
    path(
        'warehouse-account-determination/list',
        WarehouseAccountDeterminationList.as_view(),
        name='WarehouseAccountDeterminationList'
    ),
    path(
        'warehouse-account-determination/detail/<str:pk>',
        WarehouseAccountDeterminationDetail.as_view(),
        name='WarehouseAccountDeterminationDetail'
    ),
    path(
        'product-type-account-determination/list',
        ProductTypeAccountDeterminationList.as_view(),
        name='ProductTypeAccountDeterminationList'
    ),
    path(
        'product-type-account-determination/detail/<str:pk>',
        ProductTypeAccountDeterminationDetail.as_view(),
        name='ProductTypeAccountDeterminationDetail'
    ),
    path(
        'product-account-determination/list',
        ProductAccountDeterminationList.as_view(),
        name='ProductAccountDeterminationList'
    ),
    path(
        'product-account-determination/detail/<str:pk>',
        ProductAccountDeterminationDetail.as_view(),
        name='ProductAccountDeterminationDetail'
    ),
]

# Dimension
urlpatterns += [
    path('dimension-definition/list', DimensionDefinitionList.as_view(), name='DimensionDefinitionList'),
    path(
        'dimension-definition/detail/<str:pk>',
         DimensionDefinitionDetail.as_view(),
         name='DimensionDefinitionDetail'
    ),
    path(
        'dimension-definition-values/<str:pk>',
         DimensionDefinitionWithValueList.as_view(),
         name='DimensionDefinitionWithValueList'
    ),
    path('dimension-value/list', DimensionValueList.as_view(), name='DimensionValueList'),
    path('dimension-value/detail/<str:pk>', DimensionValueDetail.as_view(), name='DimensionValueDetail'),
    path('dimension-sync-config/application-list', DimensionSyncConfigApplicationList.as_view(),
         name='DimensionSyncConfigApplicationList'),
    path('dimension-sync-config/list', DimensionSyncConfigList.as_view(),
         name='DimensionSyncConfigList'),
]
