from django.urls import path
from apps.accounting.accountchart.views import AccountingAccountList

urlpatterns = [
    path('list', AccountingAccountList.as_view(), name='AccountingAccountList'),
]
