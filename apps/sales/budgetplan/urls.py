from django.urls import path
from apps.sales.budgetplan.views import (
    BudgetPlanList, BudgetPlanDetail, BudgetPlanGroupConfigList
)


urlpatterns = [
    path('list', BudgetPlanList.as_view(), name='BudgetPlanList'),
    path('detail/<str:pk>', BudgetPlanDetail.as_view(), name='BudgetPlanDetail'),
    path('budget-plan-config', BudgetPlanGroupConfigList.as_view(), name='BudgetPlanGroupConfigList'),
]
