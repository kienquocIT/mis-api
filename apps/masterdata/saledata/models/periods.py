from django.db import models
from datetime import datetime
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from apps.shared import MasterDataAbstractModel, SimpleAbstractModel


DEFINITION_INVENTORY_VALUATION_CHOICES = [
    (0, _('Perpetual inventory')),
    (1, _('Periodic inventory')),
]


class Periods(MasterDataAbstractModel):
    space_month = models.IntegerField(default=0)
    fiscal_year = models.IntegerField(null=False)
    start_date = models.DateField(null=False)
    end_date = models.DateField(null=True)
    has_revenue_planned = models.BooleanField(default=False, help_text=_('is True if has revenue planned this period'))
    has_budget_planned = models.BooleanField(default=False, help_text=_('is True if has budget planned this period'))
    sub_periods_type = models.IntegerField(choices=[(0, 'Month'), (1, 'Quarter'), (2, 'Year')], default=0)
    definition_inventory_valuation = models.SmallIntegerField(choices=DEFINITION_INVENTORY_VALUATION_CHOICES, default=0)

    @classmethod
    def get_current_period(cls, tenant_id, company_id):
        this_period = None
        for period in Periods.objects.filter(company_id=company_id, tenant_id=tenant_id).reverse():
            if period.end_date > datetime.now().date():
                this_period = period
                break
        return this_period

    @classmethod
    def get_current_sub_period(cls, this_period):
        this_sub_period = None
        for sub_period in this_period.sub_periods_period_mapped.all().reverse():
            if sub_period.end_date > datetime.now().date():
                this_sub_period = sub_period
                break
        return this_sub_period

    class Meta:
        verbose_name = 'Periods'
        verbose_name_plural = 'Periods'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class SubPeriods(SimpleAbstractModel):
    period_mapped = models.ForeignKey(Periods, on_delete=models.CASCADE, related_name='sub_periods_period_mapped')
    order = models.IntegerField()
    code = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    start_date = models.DateField(
        help_text='Sub period start date',
    )
    end_date = models.DateField(
        help_text='Sub period end date',
    )
    locked = models.BooleanField(default=0)
    run_report_inventory = models.BooleanField(default=False)

    @classmethod
    def check_period_open(cls, tenant_id, company_id):
        this_period = Periods.get_current_period(tenant_id, company_id)
        if this_period:
            this_sub_period = Periods.get_current_sub_period(this_period)
            if this_sub_period:
                if this_sub_period.locked == 0:
                    raise serializers.ValidationError(
                        {"Error": 'Can not create inventory activity now. This sub period has been Locked.'}
                    )
                return True
            raise serializers.ValidationError({"Error": 'This sub is not found.'})
        raise serializers.ValidationError({"Error": 'This period is not found.'})

    class Meta:
        verbose_name = 'Subs Period'
        verbose_name_plural = 'Subs Periods'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()
