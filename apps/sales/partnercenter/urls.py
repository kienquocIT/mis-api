from django.urls import path

from apps.sales.partnercenter.views import ListDataObjectList, ListList, ListDetail, ListResultList, ListEmployeeList, \
    ListContactList, ListIndustryList, ListOpportunityConfigStageList, ListAccountList

urlpatterns = [
    path('data-obj-list', ListDataObjectList.as_view(), name='ListDataObjectList'),
    path('list/list', ListList.as_view(), name='ListList'),
    path('list/detail/<str:pk>', ListDetail.as_view(), name='ListDetail'),
    path('list/result-list/<str:pk>', ListResultList.as_view(), name='ListResultList'),
    path('list/employee-list', ListEmployeeList.as_view(), name='ListEmployeeList'),
    path('list/contact-list', ListContactList.as_view(), name='ListContactList'),
    path('list/industry-list', ListIndustryList.as_view(), name='ListIndustryList'),
    path('list/opp-config-stage-list', ListOpportunityConfigStageList.as_view(), name='ListOpportunityConfigStageList'),
    path('list/account-list', ListAccountList.as_view(), name='ListAccountList'),
]
