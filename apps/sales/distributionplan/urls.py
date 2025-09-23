from django.urls import path
from apps.sales.distributionplan.views import (
    DistributionPlanList, DistributionPlanDetail, ProductListDistributionPlan
)

urlpatterns = [
    path('list', DistributionPlanList.as_view(), name='DistributionPlanList'),
    path('detail/<str:pk>', DistributionPlanDetail.as_view(), name='DistributionPlanDetail'),
    path('product/list/<str:pk>', ProductListDistributionPlan.as_view(), name='ProductListDistributionPlan'),
]
