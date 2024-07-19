__all__ = [
    'Group',
    'GroupLevel',
]

from typing import Union
from uuid import UUID
from django.db import models
from django.utils import timezone
from apps.core.models import TenantAbstractModel
from apps.masterdata.saledata.models import Periods
from apps.sales.budgetplan.models import BudgetPlanCompanyExpense, BudgetPlanGroupExpense


class GroupLevel(TenantAbstractModel):
    level = models.IntegerField(
        verbose_name='group level',
        null=True
    )
    description = models.CharField(
        verbose_name='group level description',
        max_length=500,
        blank=True,
        null=True
    )
    first_manager_description = models.CharField(
        verbose_name='first manager description',
        max_length=500,
        blank=True,
        null=True
    )
    second_manager_description = models.CharField(
        verbose_name='second manager description',
        max_length=500,
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Group Level'
        verbose_name_plural = 'Group Levels'
        ordering = ('level',)
        unique_together = ('company', 'level')
        default_permissions = ()
        permissions = ()


class Group(TenantAbstractModel):
    group_level = models.ForeignKey(
        'hr.GroupLevel',
        on_delete=models.CASCADE,
        null=True
    )
    parent_n = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="group_parent_n",
        verbose_name="parent group",
        null=True,
    )
    description = models.CharField(
        verbose_name='group description',
        max_length=600,
        blank=True,
        null=True
    )
    group_employee = models.JSONField(
        verbose_name="group employee",
        null=True,
        default=list
    )
    first_manager = models.ForeignKey(
        'hr.Employee',
        on_delete=models.CASCADE,
        related_name="group_first_manager",
        null=True
    )
    first_manager_title = models.CharField(
        verbose_name='first manager title',
        max_length=100,
        blank=True,
        null=True
    )
    second_manager = models.ForeignKey(
        'hr.Employee',
        on_delete=models.CASCADE,
        related_name="group_second_manager",
        null=True
    )
    second_manager_title = models.CharField(
        verbose_name='second manager title',
        max_length=100,
        blank=True,
        null=True
    )
    is_active = models.BooleanField(
        verbose_name='active status',
        default=True
    )
    is_delete = models.BooleanField(
        verbose_name='delete',
        default=False
    )

    class Meta:
        verbose_name = 'Group'
        verbose_name_plural = 'Groups'
        ordering = ('-date_created',)
        unique_together = ('company', 'code')
        default_permissions = ()
        permissions = ()

    @classmethod
    def groups_my_manager(cls, employee_id: Union[UUID, str]) -> list[str]:
        return [str(x) for x in cls.objects.filter(first_manager_id=employee_id).values_list('id', flat=True)]

    @classmethod
    def update_budget_plan(cls, budget_plan):
        BudgetPlanCompanyExpense.objects.filter(budget_plan=budget_plan).delete()
        existed_expense_id_list = []
        bulk_info = []
        order = 1
        for item in BudgetPlanGroupExpense.objects.filter(budget_plan=budget_plan).exclude(
            budget_plan_group__group_mapped=cls
        ):
            if str(item.expense_item_id) not in existed_expense_id_list:
                bulk_info.append(
                    BudgetPlanCompanyExpense(
                        order=order,
                        budget_plan=budget_plan,
                        expense_item=item.expense_item,
                        company_month_list=item.group_month_list,
                        company_quarter_list=item.group_quarter_list,
                        company_year=item.group_year
                    )
                )
                order += 1
            else:
                for data in bulk_info:
                    if str(data.expense_item_id) == str(item.expense_item_id):
                        data.company_month_list = [
                            float(mc) + float(mg) for mc, mg in
                            zip(data.company_month_list, item.group_month_list)
                        ]
                        data.company_quarter_list = [
                            float(qc) + float(qg) for qc, qg in
                            zip(data.company_quarter_list, item.group_quarter_list)
                        ]
                        data.company_year += item.group_year
            existed_expense_id_list.append(str(item.expense_item_id))
        BudgetPlanCompanyExpense.objects.bulk_create(bulk_info)
        return True

    def save(self, *args, **kwargs):
        if self.is_delete:
            this_period = Periods.objects.filter(
                tenant_id=self.tenant_id, company_id=self.company_id, fiscal_year=timezone.now().year
            ).first()
            for budget_plan in this_period.budget_plan_period_mapped.all():
                self.update_budget_plan(budget_plan)
        # hit DB
        super().save(*args, **kwargs)
