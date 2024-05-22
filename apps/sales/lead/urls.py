from django.urls import path
from apps.sales.lead.views import LeadList, LeadDetail

urlpatterns = [
    path('list', LeadList.as_view(), name='LeadList'),
    path('detail/<str:pk>', LeadDetail.as_view(), name='LeadDetail'),
]
