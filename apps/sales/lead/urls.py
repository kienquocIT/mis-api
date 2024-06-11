from django.urls import path
from apps.sales.lead.views import LeadList, LeadDetail, LeadStageList, LeadChartList, LeadListForOpportunity

urlpatterns = [
    path('list', LeadList.as_view(), name='LeadList'),
    path('list-for-opp', LeadListForOpportunity.as_view(), name='LeadListForOpportunity'),
    path('chart-data', LeadChartList.as_view(), name='LeadChartList'),
    path('detail/<str:pk>', LeadDetail.as_view(), name='LeadDetail'),
    path('list-lead-stage', LeadStageList.as_view(), name='LeadStageList'),
]
