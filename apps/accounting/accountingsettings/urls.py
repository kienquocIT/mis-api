from django.urls import path
from apps.accounting.accountingsettings.views.account_masterdata_views import (
    ChartOfAccountsList, DefaultAccountDeterminationList
)
from apps.accounting.accountingsettings.views.prd_account_deter_views import ProductAccountDeterminationList
from apps.accounting.accountingsettings.views.prd_type_account_deter_views import ProductTypeAccountDeterminationList
from apps.accounting.accountingsettings.views.wh_account_deter_views import WarehouseAccountDeterminationList

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
        'product-type-account-determination/list',
        ProductTypeAccountDeterminationList.as_view(),
        name='ProductTypeAccountDeterminationList'
    ),
    path(
        'product-account-determination/list',
        ProductAccountDeterminationList.as_view(),
        name='ProductAccountDeterminationList'
    ),
]
