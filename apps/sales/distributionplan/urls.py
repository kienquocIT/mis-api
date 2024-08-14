from django.urls import path
from apps.sales.distributionplan.views import (
    DistributionPlanList, DistributionPlanDetail
)

urlpatterns = [
    path('list', DistributionPlanList.as_view(), name='DistributionPlanList'),
    path('detail/<str:pk>', DistributionPlanDetail.as_view(), name='DistributionPlanDetail'),
]
