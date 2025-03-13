from django.urls import path
from apps.accounting.accountingsettings.views.account_masterdata_views import (
    ChartOfAccountsList, DefaultAccountDeterminationList
)
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
