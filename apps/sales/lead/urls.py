from django.urls import path
from apps.sales.lead.views import LeadList, LeadDetail, LeadStageList

urlpatterns = [
    path('list', LeadList.as_view(), name='LeadList'),
    path('detail/<str:pk>', LeadDetail.as_view(), name='LeadDetail'),
    path('list-lead-stage', LeadStageList.as_view(), name='LeadStageList'),
]
