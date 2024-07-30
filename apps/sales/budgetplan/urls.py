from django.urls import path
from apps.sales.budgetplan.views import (
    BudgetPlanList, BudgetPlanDetail, BudgetPlanGroupConfigList, ListCanViewCompanyBudgetPlan, ListCanLockBudgetPlan
)


urlpatterns = [
    path('list', BudgetPlanList.as_view(), name='BudgetPlanList'),
    path('detail/<str:pk>', BudgetPlanDetail.as_view(), name='BudgetPlanDetail'),
    path('budget-plan-config', BudgetPlanGroupConfigList.as_view(), name='BudgetPlanGroupConfigList'),
    path(
        'list-can-view-company-budget-plan',
        ListCanViewCompanyBudgetPlan.as_view(),
        name='ListCanViewCompanyBudgetPlan'
    ),
    path(
        'list-can-lock-budget-plan',
        ListCanLockBudgetPlan.as_view(),
        name='ListCanLockBudgetPlan'
    ),
]
