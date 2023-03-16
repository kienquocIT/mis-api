from django.urls import path

from apps.sale.saledata.views.accounts import (
    SalutationList, InterestsList, AccountTypeList, IndustryList,
    ContactList, ContactDetail,
    ContactListNotMapAccount,
    AccountList, AccountDetail, AccountsMapEmloyeesList,
    SalutationDetail, InterestsDetail, AccountTypeDetail, IndustryDetail,
)

urlpatterns = [
    path('salutations', SalutationList.as_view(), name='SalutationList'),
    path('salutation/<str:pk>', SalutationDetail.as_view(), name='SalutationDetail'),
    path('interests', InterestsList.as_view(), name='InterestsList'),
    path('interest/<str:pk>', InterestsDetail.as_view(), name='InterestDetail'),
    path('accounttypes', AccountTypeList.as_view(), name='AccountTypeList'),
    path('accounttype/<str:pk>', AccountTypeDetail.as_view(), name='AccountTypeDetail'),
    path('industries', IndustryList.as_view(), name='IndustryList'),
    path('industry/<str:pk>', IndustryDetail.as_view(), name='IndustryDetail'),

    # contact
    path('contacts', ContactList.as_view(), name='ContactList'),
    path('contact/<str:pk>', ContactDetail.as_view(), name='ContactDetail'),
    path('contacts-not-map-account', ContactListNotMapAccount.as_view(), name='ContactListNotMapAccount'),

    # account
    path('accounts', AccountList.as_view(), name='AccountList'),
    path('account/<str:pk>', AccountDetail.as_view(), name='AccountDetail'),
    path('accounts-map-employees', AccountsMapEmloyeesList.as_view(), name='AccountsMapEmloyeesList'),

]
