from django.db import models
from rest_framework import serializers
from apps.shared import MasterDataAbstractModel, SimpleAbstractModel


class Periods(MasterDataAbstractModel):
    space_month = models.IntegerField(default=0)
    fiscal_year = models.IntegerField(null=False)
    start_date = models.DateField(null=False)
    planned = models.BooleanField(default=False)
    sub_periods_type = models.IntegerField(choices=[(0, 'Month'), (1, 'Quarter'), (2, 'Year')], default=0)

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
    state = models.SmallIntegerField(choices=[(0, 'Open'), (1, 'Close'), (2, 'Lock')], default=0)

    @classmethod
    def check_open(cls, company_id, tenant_id, date):
        this_period = Periods.objects.filter(
            company_id=company_id, tenant_id=tenant_id, fiscal_year=date.year
        ).first()
        if this_period:
            this_sub = this_period.sub_periods_period_mapped.filter(
                order=date.month - this_period.space_month
            ).first()
            if this_sub:
                if this_sub.state == 0:
                    return True
                if this_sub.state == 1:
                    raise serializers.ValidationError(
                        {"Error": 'Can not create inventory activity now. This sub period has been Closed.'}
                    )
                if this_sub.state == 2:
                    raise serializers.ValidationError(
                        {"Error": 'Can not create inventory activity now. This sub period has been Locked.'}
                    )
            raise serializers.ValidationError({"Error": 'This sub is not found.'})
        raise serializers.ValidationError({"Error": 'This period is not found.'})

    class Meta:
        verbose_name = 'Subs Period'
        verbose_name_plural = 'Subs Periods'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()
