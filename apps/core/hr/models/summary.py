__all__ = [
    'DistributionPlan',
    'DistributionApplication',
]

from django.db import models
from django.utils import timezone

from apps.shared import SimpleAbstractModel


# PlanEmployee + PlanRole 	=> DistributionPlan
# PlanEmployeeApp + PlanRoleApp 	=> AppDistribution
# ----------------------------------------------------
# DistributionPlan
# 	employee_id
# 	plan_id
#
# ----------------------------------------------------
# AppDistribution
# 	employee_id
# 	app_id
#
# ----------------------------------------------------


class DistributionPlan(SimpleAbstractModel):
    tenant = models.ForeignKey(
        'tenant.Tenant', null=True, on_delete=models.SET_NULL,
        help_text='The tenant claims that this record belongs to them',
        related_name='%(app_label)s_%(class)s_belong_to_tenant',
    )
    company = models.ForeignKey(
        'company.Company', null=True, on_delete=models.SET_NULL,
        help_text='The company claims that this record belongs to them',
        related_name='%(app_label)s_%(class)s_belong_to_company',
    )
    tenant_plan = models.ForeignKey('tenant.TenantPlan', on_delete=models.CASCADE, verbose_name='Tenant bought plan')
    employee = models.ForeignKey('hr.Employee', on_delete=models.CASCADE, verbose_name='Distribution plan to employee')
    plan = models.ForeignKey('base.SubscriptionPlan', on_delete=models.CASCADE, verbose_name='Plan related')
    apps = models.ManyToManyField(
        'base.Application',
        through='DistributionApplication',
        symmetrical=False,
        blank=True,
        related_name='app_allowed_of_plan_distribution',
    )
    date_created = models.DateTimeField(
        default=timezone.now, editable=False,
        help_text='The record created at value',
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Distribution Plan to Employee'
        verbose_name_plural = 'Distribution Plan to Employee'
        default_permissions = ()
        permissions = ()
        unique_together = ('tenant', 'company', 'employee', 'plan')


class DistributionApplication(SimpleAbstractModel):
    distribution_plan = models.ForeignKey(DistributionPlan, on_delete=models.CASCADE, verbose_name='Distribution Plan')
    app = models.ForeignKey('base.Application', on_delete=models.CASCADE, verbose_name='Distribution app to employee')
    tenant = models.ForeignKey(
        'tenant.Tenant', null=True, on_delete=models.SET_NULL,
        help_text='The tenant claims that this record belongs to them',
        related_name='%(app_label)s_%(class)s_belong_to_tenant',
    )
    company = models.ForeignKey(
        'company.Company', null=True, on_delete=models.SET_NULL,
        help_text='The company claims that this record belongs to them',
        related_name='%(app_label)s_%(class)s_belong_to_company',
    )
    employee = models.ForeignKey('hr.Employee', on_delete=models.CASCADE, verbose_name='Distribution plan to employee')
    date_created = models.DateTimeField(
        default=timezone.now, editable=False,
        help_text='The record created at value',
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Distribution App to Employee'
        verbose_name_plural = 'Distribution App to Employee'
        default_permissions = ()
        permissions = ()
        unique_together = ('tenant', 'company', 'employee', 'app')
