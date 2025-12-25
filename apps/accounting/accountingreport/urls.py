from django.urls import path

from apps.accounting.accountingreport.views.accountbalance_report import ChartOfAccountTypeTreeList, \
    get_account_type_group
from apps.accounting.accountingreport.views.journalentry_report import JournalEntryLineList

urlpatterns = [
    path('line/list', JournalEntryLineList.as_view(), name='JournalEntryLineList'),
    path('chart-of-accounts-group-list', get_account_type_group, name='get_account_type_group'),
    path('chart-of-accounts/type-tree', ChartOfAccountTypeTreeList.as_view(), name='ChartOfAccountTypeTreeList'),
]
