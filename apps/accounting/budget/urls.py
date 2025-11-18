from django.urls import path

from .views import (BudgetLineList, BudgetList)

urlpatterns = [
    path('list', BudgetList.as_view(), name='BudgetList'),
    path('budget-line/list', BudgetLineList.as_view(), name='BudgetLineList'),
]
