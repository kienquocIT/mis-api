from django.urls import path

from .views import (BudgetLineList)

urlpatterns = [
    path('budget-line/list', BudgetLineList.as_view(), name='BudgetLineList'),
]
