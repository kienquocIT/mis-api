from django.urls import path
from apps.accounting.accountingsettings.views import ChartOfAccountsList, DefaultAccountDefinitionList

urlpatterns = [
    path('chart-of-accounts', ChartOfAccountsList.as_view(), name='ChartOfAccountsList'),
    path('default-account-definition', DefaultAccountDefinitionList.as_view(), name='DefaultAccountDefinitionList'),
]
