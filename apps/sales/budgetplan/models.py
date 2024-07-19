from django.db import models
from apps.shared import DataAbstractModel, SimpleAbstractModel


class BudgetPlan(DataAbstractModel):
    period_mapped = models.ForeignKey('saledata.Periods', on_delete=models.CASCADE)
    monthly = models.BooleanField(default=False)
    quarterly = models.BooleanField(default=False)
    auto_sum_target = models.BooleanField(default=False)
    is_lock = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Budget Plan'
        verbose_name_plural = 'Budget Plans'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class BudgetPlanGroup(SimpleAbstractModel):
    budget_plan = models.ForeignKey(
        BudgetPlan,
        on_delete=models.CASCADE,
        related_name='budget_plan_group_budget_plan'
    )
    group_mapped = models.ForeignKey('hr.Group', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Budget Plan Group'
        verbose_name_plural = 'Budget Plan Groups'
        ordering = ()
        default_permissions = ()
        permissions = ()


class BudgetPlanCompanyExpense(SimpleAbstractModel):
    order = models.IntegerField(default=0)
    budget_plan = models.ForeignKey(
        BudgetPlan,
        on_delete=models.CASCADE,
        related_name='budget_plan_company_expense_budget_plan'
    )
    expense_item = models.ForeignKey(
        'saledata.ExpenseItem',
        on_delete=models.CASCADE,
        related_name='budget_plan_company_expense_expense_item'
    )
    company_month_list = models.JSONField(default=list)  # [number * 12]
    company_quarter_list = models.JSONField(default=list)  # [number * 4]
    company_year = models.FloatField(default=0)

    class Meta:
        verbose_name = 'Budget Plan Company'
        verbose_name_plural = 'Budget Plan Companies'
        ordering = ()
        default_permissions = ()
        permissions = ()


class BudgetPlanGroupExpense(SimpleAbstractModel):
    order = models.IntegerField(default=0)
    budget_plan = models.ForeignKey(
        BudgetPlan,
        on_delete=models.CASCADE,
        related_name='budget_plan_group_expense_budget_plan'
    )
    budget_plan_group = models.ForeignKey(
        BudgetPlanGroup,
        on_delete=models.CASCADE,
        related_name='budget_plan_group_expense_budget_plan_group'
    )
    expense_item = models.ForeignKey(
        'saledata.ExpenseItem',
        on_delete=models.CASCADE,
        related_name='budget_plan_group_expense_expense_item'
    )
    group_month_list = models.JSONField(default=list)  # [number * 12]
    group_quarter_list = models.JSONField(default=list)  # [number * 4]
    group_year = models.FloatField(default=0)

    class Meta:
        verbose_name = 'Budget Plan Group Expense'
        verbose_name_plural = 'Budget Plans Groups Expenses'
        ordering = ()
        default_permissions = ()
        permissions = ()
