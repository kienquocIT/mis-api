from django.urls import path
from apps.accounting.accountingsettings.views import ChartOfAccountsList, DefaultAccountDefinitionList

urlpatterns = [
    path('chart-of-accounts/list', ChartOfAccountsList.as_view(), name='ChartOfAccountsList'),
    path('default-account-definition/list', DefaultAccountDefinitionList.as_view(), name='DefaultAccountDefinitionList'),
]
