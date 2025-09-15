from django.urls import path
from .views import (
    OpportunityList, OpportunityDetail,
    OpportunityCallLogList, OpportunityCallLogDetail,
    OpportunityEmailList, OpportunityEmailDetail,
    OpportunityMeetingList, OpportunityMeetingDetail,
    OpportunityDocumentList, OpportunityDocumentDetail,
    OpportunityActivityLogList,
    OpportunityConfigDetail,
    OpportunityConfigStageList, OpportunityConfigStageDetail, OpportunityStageChecking,
    CustomerDecisionFactorList,
    CustomerDecisionFactorDetail,
    OpportunityMemberDetail, OpportunityMemberList,
)

urlpatterns = [
    # main
    path('list', OpportunityList.as_view(), name='OpportunityList'),
    path('detail/<str:pk>', OpportunityDetail.as_view(), name='OpportunityDetail'),
    # activities
    path('call-log/list', OpportunityCallLogList.as_view(), name='OpportunityCallLogList'),
    path('call-log/<str:pk>', OpportunityCallLogDetail.as_view(), name='OpportunityCallLogDetail'),
    path('send-email/list', OpportunityEmailList.as_view(), name='OpportunityEmailList'),
    path('send-email/<str:pk>', OpportunityEmailDetail.as_view(), name='OpportunityEmailDetail'),
    path('meeting/list', OpportunityMeetingList.as_view(), name='OpportunityMeetingList'),
    path('meeting/<str:pk>', OpportunityMeetingDetail.as_view(), name='OpportunityMeetingDetail'),
    path('document/list', OpportunityDocumentList.as_view(), name='OpportunityDocumentList'),
    path('document/<str:pk>', OpportunityDocumentDetail.as_view(), name='OpportunityDocumentDetail'),
    path('activity-log/list', OpportunityActivityLogList.as_view(), name='OpportunityActivityLogList'),
    # config
    path('config-detail', OpportunityConfigDetail.as_view(), name='OpportunityConfigDetail'),
    # stage
    path('stage/list', OpportunityConfigStageList.as_view(), name='OpportunityConfigStageList'),
    path('stage/<str:pk>', OpportunityConfigStageDetail.as_view(), name='OpportunityConfigStageDetail'),
    path('stage-checking', OpportunityStageChecking.as_view(), name='OpportunityStageChecking'),
    # related
    path('decision-factor/list', CustomerDecisionFactorList.as_view(), name='CustomerDecisionFactorList'),
    path('decision-factor/<str:pk>', CustomerDecisionFactorDetail.as_view(), name='CustomerDecisionFactorDetail'),
    path('detail/<str:pk_opp>/member/list', OpportunityMemberList.as_view(), name='OpportunityMemberList'),
    path('detail/<str:pk_opp>/member/<str:pk_member>', OpportunityMemberDetail.as_view(), name='OpportunityMemberDetail'),
]
