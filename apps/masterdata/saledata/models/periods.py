from datetime import datetime
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from apps.core.company.models import Company
from apps.shared import MasterDataAbstractModel, SimpleAbstractModel


DEFINITION_INVENTORY_VALUATION_CHOICES = [
    (0, _('Perpetual inventory')),
    (1, _('Periodic inventory')),
]

DEFAULT_INVENTORY_VALUE_METHOD_CHOICES = [
    (0, _('FIFO')),
    (1, _('Weighted average')),
    (2, _('Specific identification')),
]

ACCOUNTING_POLICIES_CHOICES = [
    (0, _('VAS')),
    (1, _('IAS')),
]

APPLICABLE_CIRCULAR_CHOICES = [
    (0, '200/2014/TT-BTC'),
    (1, '133/2015/TT-BTC'),
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
    default_inventory_value_method = models.SmallIntegerField(choices=DEFAULT_INVENTORY_VALUE_METHOD_CHOICES, default=1)
    cost_per_warehouse = models.BooleanField(default=True)
    cost_per_lot = models.BooleanField(default=False)
    cost_per_project = models.BooleanField(default=False)
    accounting_policies = models.SmallIntegerField(choices=ACCOUNTING_POLICIES_CHOICES, default=0)
    applicable_circular = models.SmallIntegerField(choices=APPLICABLE_CIRCULAR_CHOICES, default=0)
    currency_mapped = models.ForeignKey(
        'saledata.Currency',
        on_delete=models.CASCADE,
        null=True,
        related_name='period_currency_mapped'
    )

    @classmethod
    def get_period_by_doc_date(cls, tenant_id, company_id, doc_date):
        period_by_doc_date = None
        for period in Periods.objects.filter(company_id=company_id, tenant_id=tenant_id).order_by('fiscal_year'):
            if period.end_date >= doc_date.date() >= period.start_date:
                period_by_doc_date = period
                break
        return period_by_doc_date

    @classmethod
    def get_sub_period_by_doc_date(cls, period, doc_date):
        this_sub_period = None
        for sub_period in period.sub_periods_period_mapped.all().order_by('order'):
            if sub_period.end_date >= doc_date.date() >= sub_period.start_date:
                this_sub_period = sub_period
                break
        return this_sub_period

    @classmethod
    def get_current_period(cls, tenant_id, company_id):
        this_period = None
        for period in Periods.objects.filter(company_id=company_id, tenant_id=tenant_id).order_by('fiscal_year'):
            if period.end_date >= datetime.now().date() >= period.start_date:
                this_period = period
                break
        return this_period

    @classmethod
    def get_current_sub_period(cls, this_period):
        this_sub_period = None
        for sub_period in this_period.sub_periods_period_mapped.all().order_by('order'):
            if sub_period.end_date >= datetime.now().date() >= sub_period.start_date:
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
    def check_period(cls, tenant_id, company_id):
        """
        Kiểm tra thử năm tài chính hiện tại có hay chưa?
        Lưu ý: chỉ sử dụng tham số 'skip_check_period' để bỏ qua hàm này khi chạy các script để tránh sai dữ liệu
        """
        company_obj = Company.objects.filter(id=company_id).first()
        if not company_obj:
            raise serializers.ValidationError({"Error": "[check_period] Company is not found."})

        software_start_using_time = company_obj.software_start_using_time
        if not software_start_using_time:
            raise serializers.ValidationError({"Error": "[check_period] Software start using time is not found."})

        if software_start_using_time.date() > timezone.now().date():
            raise serializers.ValidationError({
                "Error": f"[check_period] Cannot create an inventory activity before Software start using time "
                         f"({software_start_using_time.date()})"
            })

        this_period = Periods.get_current_period(tenant_id, company_id)
        if not this_period:
            raise serializers.ValidationError({"Error": "[check_period] Current period is not found."})

        this_sub_period = Periods.get_current_sub_period(this_period)
        if not this_sub_period:
            raise serializers.ValidationError({"Error": "[check_period] Current sub period is not found."})

        if this_sub_period.locked:
            raise serializers.ValidationError({
                "Error": "[check_period] Cannot create an inventory activity now. Current sub period has been Locked."
            })

        return True

    class Meta:
        verbose_name = 'Subs Period'
        verbose_name_plural = 'Subs Periods'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()
