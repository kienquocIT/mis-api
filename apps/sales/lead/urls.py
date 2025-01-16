from django.urls import path
from apps.sales.lead.views import LeadList, LeadDetail, LeadStageList, LeadChartList, LeadListForOpportunity, \
    LeadCallList, LeadActivityList, LeadEmailList, LeadMeetingList, LeadCallDetail, LeadMeetingDetail

urlpatterns = [
    path('list', LeadList.as_view(), name='LeadList'),
    path('list-for-opp', LeadListForOpportunity.as_view(), name='LeadListForOpportunity'),
    path('chart-data', LeadChartList.as_view(), name='LeadChartList'),
    path('detail/<str:pk>', LeadDetail.as_view(), name='LeadDetail'),
    path('list-lead-stage', LeadStageList.as_view(), name='LeadStageList'),

    path('call/list', LeadCallList.as_view(), name='LeadCallList'),
    path('call/detail/<str:pk>', LeadCallDetail.as_view(), name='LeadCallDetail'),
    path('email/list', LeadEmailList.as_view(), name='LeadEmailList'),
    path('meeting/list', LeadMeetingList.as_view(), name='LeadMeetingList'),
    path('meeting/detail/<str:pk>', LeadMeetingDetail.as_view(), name='LeadMeetingDetail'),
    path('activity/list', LeadActivityList.as_view(), name='LeadActivityList'),
]
