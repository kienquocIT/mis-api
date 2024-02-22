from django.db import models
from apps.shared import DataAbstractModel, SimpleAbstractModel


PROFIT_TARGET_TYPE = (
    (0, 'Gross profit'),
    (1, 'Net income'),
)


class RevenuePlan(DataAbstractModel):
    period_mapped = models.ForeignKey('saledata.Periods', on_delete=models.CASCADE)
    group_mapped_list = models.JSONField(default=list)  # [id, id, id]
    monthly = models.BooleanField(default=False)
    quarterly = models.BooleanField(default=False)
    auto_sum_target = models.BooleanField(default=False)
    company_month_target = models.JSONField(default=list)  # [number * 12]
    company_quarter_target = models.JSONField(default=list)  # [number * 4]
    company_year_target = models.FloatField(default=0)

    profit_target_type = models.SmallIntegerField(default=0, choices=PROFIT_TARGET_TYPE)
    company_month_profit_target = models.JSONField(default=list)  # [number * 12]
    company_quarter_profit_target = models.JSONField(default=list)  # [number * 4]
    company_year_profit_target = models.FloatField(default=0)

    class Meta:
        verbose_name = 'Revenue Plan'
        verbose_name_plural = 'Revenue Plans'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class RevenuePlanGroup(SimpleAbstractModel):
    revenue_plan_mapped = models.ForeignKey(
        RevenuePlan,
        on_delete=models.CASCADE,
        related_name='revenue_plan_mapped_group'
    )
    group_mapped = models.ForeignKey('hr.Group', on_delete=models.CASCADE)
    group_month_target = models.JSONField(default=list)  # [number * 12]
    group_quarter_target = models.JSONField(default=list)  # [number * 4]
    group_year_target = models.FloatField(default=0)
    group_month_profit_target = models.JSONField(default=list)  # [number * 12]
    group_quarter_profit_target = models.JSONField(default=list)  # [number * 4]
    group_year_profit_target = models.FloatField(default=0)
    employee_mapped_list = models.JSONField(default=list)  # [id, id, id]

    class Meta:
        verbose_name = 'Revenue Plan Group'
        verbose_name_plural = 'Revenue Plans Groups'
        ordering = ()
        default_permissions = ()
        permissions = ()


class RevenuePlanGroupEmployee(SimpleAbstractModel):
    revenue_plan_mapped = models.ForeignKey(
        RevenuePlan,
        on_delete=models.CASCADE,
        related_name='revenue_plan_mapped_group_employee',
    )
    revenue_plan_group_mapped = models.ForeignKey(
        'hr.Group',
        on_delete=models.CASCADE,
        related_name='revenue_plan_group_mapped'
    )
    emp_month_target = models.JSONField(default=list)  # [number * 12]
    emp_quarter_target = models.JSONField(default=list)  # [number * 4]
    emp_year_target = models.FloatField(default=0)
    emp_month_profit_target = models.JSONField(default=list)  # [number * 12]
    emp_quarter_profit_target = models.JSONField(default=list)  # [number * 4]
    emp_year_profit_target = models.FloatField(default=0)
    employee_mapped = models.ForeignKey('hr.Employee', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Revenue Plan Group Employee'
        verbose_name_plural = 'Revenue Plans Groups Employees'
        ordering = ()
        default_permissions = ()
        permissions = ()
