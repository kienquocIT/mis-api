from django.urls import path
from apps.sales.revenue_plan.views import (
    RevenuePlanDetail, RevenuePlanList, RevenuePlanByReportPermList
)


urlpatterns = [
    path('list', RevenuePlanList.as_view(), name='RevenuePlanList'),
    path('detail/<str:pk>', RevenuePlanDetail.as_view(), name='RevenuePlanDetail'),
    path('list-by-report-perm', RevenuePlanByReportPermList.as_view(), name='RevenuePlanByReportPermList'),
]
