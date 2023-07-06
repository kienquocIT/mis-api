from django.urls import path

from .views import (
    OpportunityList, OpportunityDetail, CustomerDecisionFactorList, OpportunityConfigDetail,
    CustomerDecisionFactorDetail, OpportunityConfigStageList, OpportunityConfigStageDetail,
    OpportunityCallLogList, OpportunityCallLogDetail
)

urlpatterns = [
    path('config', OpportunityConfigDetail.as_view(), name='OpportunityConfigDetail'),
    path('lists', OpportunityList.as_view(), name='OpportunityList'),
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
]
