from django.urls import path

from .views.opportunity import OpportunityList, OpportunityDetail

urlpatterns = [
    path('lists', OpportunityList.as_view(), name='OpportunityList'),
    path('<str:pk>', OpportunityDetail.as_view(), name='OpportunityDetail'),
]
