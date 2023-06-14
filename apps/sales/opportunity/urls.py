from django.urls import path

from .views import OpportunityList, OpportunityDetail, CustomerDecisionFactorList, OpportunityConfigDetail, \
    CustomerDecisionFactorDetail

urlpatterns = [
    path('config', OpportunityConfigDetail.as_view(), name='OpportunityConfigDetail'),
    path('lists', OpportunityList.as_view(), name='OpportunityList'),
    path('<str:pk>', OpportunityDetail.as_view(), name='OpportunityDetail'),

    path('config/decision-factors', CustomerDecisionFactorList.as_view(), name='CustomerDecisionFactorList'),
    path(
        'config/decision-factor/<str:pk>', CustomerDecisionFactorDetail.as_view(), name='CustomerDecisionFactorDetail'
    ),
]
