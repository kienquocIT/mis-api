from django.urls import path
from apps.accounting.accountingsettings.views.chart_of_account import (
    ChartOfAccountsList
)
from apps.accounting.accountingsettings.views.account_determination import (
    AccountDeterminationList, AccountDeterminationDetail
)
from apps.accounting.accountingsettings.views.dimension import (
    DimensionDefinitionList, DimensionDefinitionDetail,
    DimensionDefinitionWithValueList, DimensionValueList, DimensionValueDetail, DimensionSyncConfigApplicationList,
    DimensionSyncConfigList, DimensionSyncConfigDetail, DimensionListForAccountingAccount, DimensionAccountMapList,
    DimensionAccountMapDetail, DimensionSplitTemplateList
)
from apps.accounting.accountingsettings.views.product_account_determination import (
    ProductAccountDeterminationList, ProductAccountDeterminationDetail
)
from apps.accounting.accountingsettings.views.product_type_account_determination import (
    ProductTypeAccountDeterminationList, ProductTypeAccountDeterminationDetail
)
from apps.accounting.accountingsettings.views.warehouse_account_determination import (
    WarehouseAccountDeterminationList, WarehouseAccountDeterminationDetail
)


urlpatterns = [
    path('chart-of-accounts/list', ChartOfAccountsList.as_view(), name='ChartOfAccountsList'),
    path('account-determination/list', AccountDeterminationList.as_view(), name='AccountDeterminationList'),
    path(
        'account-determination/detail/<str:pk>',
        AccountDeterminationDetail.as_view(),
        name='AccountDeterminationDetail'
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
] + [
    # Dimension
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
    path('dimension-sync-config/detail/<str:pk>', DimensionSyncConfigDetail.as_view(),
         name='DimensionSyncConfigDetail'),
    path('dimension-for-account/detail/<str:pk>', DimensionListForAccountingAccount.as_view(),
         name='DimensionListForAccountingAccount'),
    path('dimension-account-map/list', DimensionAccountMapList.as_view(), name='DimensionAccountMapList'),
    path('dimension-account-map/detail/<str:pk>', DimensionAccountMapDetail.as_view(),
         name='DimensionAccountMapDetail'),
    path('dimension-split-template/list', DimensionSplitTemplateList.as_view(), name='DimensionSplitTemplateList'),
    # path('dimension-split-template/detail/<str:pk>', DimensionAccountMapDetail.as_view(),
    #      name='DimensionAccountMapDetail'),
]
