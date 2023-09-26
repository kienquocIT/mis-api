from django.urls import path

from .views import (
    OpportunityList, OpportunityDetail, CustomerDecisionFactorList, OpportunityConfigDetail,
    CustomerDecisionFactorDetail, OpportunityConfigStageList, OpportunityConfigStageDetail,
    OpportunityCallLogList, OpportunityCallLogDetail, OpportunityCallLogDelete,
    OpportunityEmailList, OpportunityEmailDetail, OpportunityEmailDelete,
    OpportunityMeetingList, OpportunityMeetingDetail, OpportunityMeetingDelete, OpportunityDocumentList,
    OpportunityDocumentDetail, OpportunityActivityLogList, OpportunityForSaleList, OpportunityMemberDetail,
    OpportunityAddMember, OpportunityDeleteMember, MemberPermissionUpdateSerializer, OpportunityMemberList
)

urlpatterns = [
    path('config', OpportunityConfigDetail.as_view(), name='OpportunityConfigDetail'),
    path('lists', OpportunityList.as_view(), name='OpportunityList'),
    path('lists-sale', OpportunityForSaleList.as_view(), name='OpportunityForSaleList'),
    path('<str:pk>', OpportunityDetail.as_view(), name='OpportunityDetail'),

    path('config/decision-factors', CustomerDecisionFactorList.as_view(), name='CustomerDecisionFactorList'),
    path(
        'config/decision-factor/<str:pk>', CustomerDecisionFactorDetail.as_view(), name='CustomerDecisionFactorDetail'
    ),
    path('config/stage', OpportunityConfigStageList.as_view(), name='OpportunityConfigStageList'),
    path('config/stage/<str:pk>', OpportunityConfigStageDetail.as_view(), name='OpportunityConfigStageDetail'),
] + [
    path('call-log/lists', OpportunityCallLogList.as_view(), name='OpportunityCallLogList'),
    path('call-log/<str:pk>', OpportunityCallLogDetail.as_view(), name='OpportunityCallLogDetail'),
    path('delete-call-log/<str:pk>', OpportunityCallLogDelete.as_view(), name='OpportunityCallLogDelete'),
] + [
    path('send-email/lists', OpportunityEmailList.as_view(), name='OpportunityEmailList'),
    path('send-email/<str:pk>', OpportunityEmailDetail.as_view(), name='OpportunityEmailDetail'),
    path('delete-email/<str:pk>', OpportunityEmailDelete.as_view(), name='OpportunityEmailDelete'),
] + [
    path('meeting/lists', OpportunityMeetingList.as_view(), name='OpportunityMeetingList'),
    path('meeting/<str:pk>', OpportunityMeetingDetail.as_view(), name='OpportunityMeetingDetail'),
    path('delete-meeting/<str:pk>', OpportunityMeetingDelete.as_view(), name='OpportunityMeetingDelete'),
] + [
    path('document/list', OpportunityDocumentList.as_view(), name='OpportunityDocumentList'),
    path('document/<str:pk>', OpportunityDocumentDetail.as_view(), name='OpportunityDocumentDetail'),
] + [  # opportunity activity log
    path('activity-log/lists', OpportunityActivityLogList.as_view(), name='OpportunityActivityLogList'),
] + [  # member detail
    path('member/detail/<str:pk>', OpportunityMemberDetail.as_view(), name='OpportunityMemberDetail'),
    path('add-member/<str:pk>', OpportunityAddMember.as_view(), name='OpportunityAddMember'),
    path('member/delete/<str:pk>', OpportunityDeleteMember.as_view(), name='OpportunityDeleteMember'),
    path(
        'member/set/permission/<str:pk>',
        MemberPermissionUpdateSerializer.as_view(),
        name='MemberPermissionUpdateSerializer'
    ),
    path('member/list/<str:pk>', OpportunityMemberList.as_view(), name='OpportunityMemberList'),
]
