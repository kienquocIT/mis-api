from django.urls import path
from apps.accounting.accountingsettings.views import ChartOfAccountsList, DefaultAccountDeterminationList

urlpatterns = [
    path('chart-of-accounts/list', ChartOfAccountsList.as_view(), name='ChartOfAccountsList'),
    path(
        'default-account-determination/list',
        DefaultAccountDeterminationList.as_view(),
        name='DefaultAccountDeterminationList'
    ),
]
