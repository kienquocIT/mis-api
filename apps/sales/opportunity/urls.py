from django.urls import path

from .views import OpportunityList, OpportunityDetail, OpportunityDecisionFactorList

urlpatterns = [
    path('lists', OpportunityList.as_view(), name='OpportunityList'),
    path('<str:pk>', OpportunityDetail.as_view(), name='OpportunityDetail'),

    path('config/decision-factor/lists', OpportunityDecisionFactorList.as_view(), name='OpportunityDecisionFactorList'),
]
