from django.urls import path, include

from apps.sale.saledata.views.accounts import (
    SalutationList, InterestsList, AccountTypeList, IndustryList,

    ContactList, ContactDraftList, ContactDetail, ContactDraftDetail,
    ContactListNotMapAccount,

    AccountList, AccountDetail, EmployeeMapAccountList
)

urlpatterns = [
    path('contact/salutation/list', SalutationList.as_view(), name='SalutationList'),
    path('contact/interest/list', InterestsList.as_view(), name='InterestsList'),
    path('account/accounttype/list', AccountTypeList.as_view(), name='AccountTypeList'),
    path('account/industry/list', IndustryList.as_view(), name='IndustryList'),

    # contact
    path('list', ContactList.as_view(), name='ContactList'),
    path('list/<str:pk>', ContactDetail.as_view(), name='ContactDetail'),
    path('listnotmapaccount', ContactListNotMapAccount.as_view(), name='ContactListNotMapAccount'),

    path('draft/list', ContactDraftList.as_view(), name='ContactDraftList'),
    path('draft/list/<str:pk>', ContactDraftDetail.as_view(), name='ContactDraftDetail'),

    # account
    path('list', AccountList.as_view(), name='AccountList'),
    path('list/<str:pk>', AccountDetail.as_view(), name='AccountDetail'),
    path('employee_map_account_list', EmployeeMapAccountList.as_view(), name='EmployeeMapAccountList'),
]