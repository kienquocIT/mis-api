from django.urls import path
from apps.accounting.accountingsettings.views.chart_of_account import (
    ChartOfAccountsList
)
from apps.accounting.accountingsettings.views.account_determination import (
    AccountDeterminationList, AccountDeterminationDetail
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
    path(
        'account-determination/list',
        AccountDeterminationList.as_view(),
        name='AccountDeterminationList'
    ),
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
]
