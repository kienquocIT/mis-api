from django.urls import path

from .views import (ReportRevenueList)

urlpatterns = [
    path('revenue/list', ReportRevenueList.as_view(), name='ReportRevenueList'),
]
