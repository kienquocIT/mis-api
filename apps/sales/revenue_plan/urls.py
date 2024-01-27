from django.urls import path
from apps.sales.revenue_plan.views import (
    RevenuePlanDetail, RevenuePlanList
)


urlpatterns = [
    path('list', RevenuePlanList.as_view(), name='RevenuePlanList'),
    path('detail/<str:pk>', RevenuePlanDetail.as_view(), name='RevenuePlanDetail'),
]
