from django.urls import path, include

from apps.sale.saledata.views.accounts import (
    SalutationList, InterestsList, AccountTypeList, IndustryList,
    ContactList, ContactDetail,
    ContactListNotMapAccount,
    AccountList, AccountDetail, EmployeeMapAccountList
)

urlpatterns = [
    path('salurations', SalutationList.as_view(), name='SalutationList'),
    path('interests', InterestsList.as_view(), name='InterestsList'),
    path('accounttypes', AccountTypeList.as_view(), name='AccountTypeList'),
    path('industries;', IndustryList.as_view(), name='IndustryList'),

    # contact
    path('contacts', ContactList.as_view(), name='ContactList'),
    path('contact/<str:pk>', ContactDetail.as_view(), name='ContactDetail'),
    path('listnotmapaccount', ContactListNotMapAccount.as_view(), name='ContactListNotMapAccount'),

    # account
    path('accounts', AccountList.as_view(), name='AccountList'),
    path('account/<str:pk>', AccountDetail.as_view(), name='AccountDetail'),
    path('employee_map_account_list', EmployeeMapAccountList.as_view(), name='EmployeeMapAccountList'),
]
