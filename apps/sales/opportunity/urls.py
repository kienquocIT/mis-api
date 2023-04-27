from django.urls import path

from .views import OpportunityList, OpportunityDetail

urlpatterns = [
    path('lists', OpportunityList.as_view(), name='OpportunityList'),
    path('<str:pk>', OpportunityDetail.as_view(), name='OpportunityDetail'),
]
