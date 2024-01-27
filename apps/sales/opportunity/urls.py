from django.urls import path

from .views import (
    OpportunityList, OpportunityDetail, CustomerDecisionFactorList, OpportunityConfigDetail,
    CustomerDecisionFactorDetail, OpportunityConfigStageList, OpportunityConfigStageDetail,
    OpportunityCallLogList, OpportunityCallLogDetail,
    OpportunityEmailList, OpportunityEmailDetail,
    OpportunityMeetingList, OpportunityMeetingDetail,
    OpportunityDocumentList, OpportunityDocumentDetail,
    OpportunityActivityLogList, OpportunityForSaleList,
    MemberOfOpportunityDetail, MemberOfOpportunityDetailAdd, OpportunityDetailGetByCreateFromOpp,
)

urlpatterns = [
    path('config', OpportunityConfigDetail.as_view(), name='OpportunityConfigDetail'),
    path('lists', OpportunityList.as_view(), name='OpportunityList'),
    path('lists-sale', OpportunityForSaleList.as_view(), name='OpportunityForSaleList'),
    path(
        '<str:pk>/create-from-opp',
        OpportunityDetailGetByCreateFromOpp.as_view(), name='OpportunityDetailGetByCreateFromOpp'
    ),
    path('<str:pk>', OpportunityDetail.as_view(), name='OpportunityDetail'),
    path('<str:pk_opp>/member/add', MemberOfOpportunityDetailAdd.as_view(), name='MemberOfOpportunityDetailAdd'),
    path('<str:pk_opp>/member/<str:pk_member>', MemberOfOpportunityDetail.as_view(), name='MemberOfOpportunityDetail'),

    path('config/decision-factors', CustomerDecisionFactorList.as_view(), name='CustomerDecisionFactorList'),
    path(
        'config/decision-factor/<str:pk>', CustomerDecisionFactorDetail.as_view(), name='CustomerDecisionFactorDetail'
    ),
    path('config/stage', OpportunityConfigStageList.as_view(), name='OpportunityConfigStageList'),
    path('config/stage/<str:pk>', OpportunityConfigStageDetail.as_view(), name='OpportunityConfigStageDetail'),
] + [
    path('call-log/lists', OpportunityCallLogList.as_view(), name='OpportunityCallLogList'),
    path('call-log/<str:pk>', OpportunityCallLogDetail.as_view(), name='OpportunityCallLogDetail'),
] + [
    path('send-email/lists', OpportunityEmailList.as_view(), name='OpportunityEmailList'),
    path('send-email/<str:pk>', OpportunityEmailDetail.as_view(), name='OpportunityEmailDetail'),
] + [
    path('meeting/lists', OpportunityMeetingList.as_view(), name='OpportunityMeetingList'),
    path('meeting/<str:pk>', OpportunityMeetingDetail.as_view(), name='OpportunityMeetingDetail'),
] + [
    path('document/list', OpportunityDocumentList.as_view(), name='OpportunityDocumentList'),
    path('document/<str:pk>', OpportunityDocumentDetail.as_view(), name='OpportunityDocumentDetail'),
] + [  # opportunity activity log
    path('activity-log/lists', OpportunityActivityLogList.as_view(), name='OpportunityActivityLogList'),
]
