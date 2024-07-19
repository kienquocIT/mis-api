from django.urls import path
from apps.sales.budgetplan.views import (
    BudgetPlanList, BudgetPlanDetail
)


urlpatterns = [
    path('list', BudgetPlanList.as_view(), name='BudgetPlanList'),
    path('detail/<str:pk>', BudgetPlanDetail.as_view(), name='BudgetPlanDetail'),
]
