from django.db import models

from apps.shared import DataAbstractModel, MasterDataAbstractModel, ACCEPTANCE_AFFECT_BY


class FinalAcceptance(DataAbstractModel):
    sale_order = models.OneToOneField(
        'saleorder.SaleOrder',
        on_delete=models.CASCADE,
        verbose_name="sale order",
        related_name="final_acceptance_sale_order",
    )
    opportunity = models.ForeignKey(
        'opportunity.Opportunity',
        on_delete=models.CASCADE,
        verbose_name="opportunity",
        related_name="final_acceptance_opportunity",
        null=True,
    )

    @classmethod
    def find_max_number(cls, codes):
        num_max = None
        for code in codes:
            try:
                if code != '':
                    tmp = int(code.split('-', maxsplit=1)[0].split("FA")[1])
                    if num_max is None or (isinstance(num_max, int) and tmp > num_max):
                        num_max = tmp
            except Exception as err:
                print(err)
        return num_max

    @classmethod
    def generate_code(cls, company_id):
        existing_codes = cls.objects.filter(company_id=company_id).values_list('code', flat=True)
        num_max = cls.find_max_number(existing_codes)
        if num_max is None:
            code = 'FA0001'
        elif num_max < 10000:
            num_str = str(num_max + 1).zfill(4)
            code = f'FA{num_str}'
        else:
            raise ValueError('Out of range: number exceeds 10000')
        if cls.objects.filter(code=code, company_id=company_id).exists():
            return cls.generate_code(company_id=company_id)
        return code

    @classmethod
    def push_final_acceptance(
            cls,
            tenant_id,
            company_id,
            sale_order_id,
            employee_created_id,
            employee_inherit_id,
            opportunity_id,
            list_data_indicator: list,
    ):
        obj, _created = cls.objects.get_or_create(
            tenant_id=tenant_id, company_id=company_id, sale_order_id=sale_order_id,
            defaults={
                'employee_created_id': employee_created_id,
                'employee_inherit_id': employee_inherit_id,
                'opportunity_id': opportunity_id,
            }
        )
        list_indicator = [
            FinalAcceptanceIndicator(
                final_acceptance=obj,
                **data_indicator,
            )
            for data_indicator in list_data_indicator
        ]
        FinalAcceptanceIndicator.create_final_acceptance_indicators(list_indicator=list_indicator)
        return True

    def save(self, *args, **kwargs):
        if self.system_status in [2, 3]:  # added, finish
            # check if not code then generate code
            if not self.code:
                self.code = self.generate_code(self.company_id)
                if 'update_fields' in kwargs:
                    if isinstance(kwargs['update_fields'], list):
                        kwargs['update_fields'].append('code')
                else:
                    kwargs.update({'update_fields': ['code']})
        # hit DB
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Final Acceptance'
        verbose_name_plural = 'Final Acceptances'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class FinalAcceptanceIndicator(MasterDataAbstractModel):
    final_acceptance = models.ForeignKey(
        FinalAcceptance,
        on_delete=models.CASCADE,
        verbose_name="final acceptance",
        related_name="fa_indicator_final_acceptance",
    )
    sale_order_indicator = models.OneToOneField(
        'saleorder.SaleOrderIndicator',
        on_delete=models.CASCADE,
        null=True
    )
    indicator = models.ForeignKey(
        'quotation.QuotationIndicatorConfig',
        on_delete=models.CASCADE,
        verbose_name="indicator",
        related_name="fa_indicator_indicator",
        null=True
    )
    sale_order = models.ForeignKey(
        'saleorder.SaleOrder',
        on_delete=models.CASCADE,
        verbose_name="sale order",
        related_name="fa_indicator_sale_order",
        null=True,
    )
    payment = models.ForeignKey(
        'cashoutflow.Payment',
        on_delete=models.CASCADE,
        verbose_name="payment",
        related_name="fa_indicator_payment",
        null=True,
    )
    expense_item = models.ForeignKey(
        'saledata.ExpenseItem',
        on_delete=models.CASCADE,
        verbose_name="expense item",
        related_name="fa_indicator_expense_item",
        null=True,
    )
    labor_item = models.ForeignKey(
        'saledata.Expense',
        on_delete=models.CASCADE,
        verbose_name="labor item",
        related_name="fa_indicator_labor_item",
        null=True
    )
    delivery_sub = models.ForeignKey(
        'delivery.OrderDeliverySub',
        on_delete=models.CASCADE,
        verbose_name="delivery sub",
        related_name="fa_indicator_delivery_sub",
        null=True,
    )
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        verbose_name="product",
        related_name="fa_indicator_product",
        null=True
    )
    indicator_value = models.FloatField(default=0)
    actual_value = models.FloatField(default=0)
    actual_value_after_tax = models.FloatField(default=0)
    different_value = models.FloatField(default=0)
    rate_value = models.FloatField(default=0)
    remark = models.CharField(verbose_name='remark', max_length=500, blank=True, null=True,)
    order = models.IntegerField(default=1)
    acceptance_affect_by = models.SmallIntegerField(
        default=1,
        help_text='choices= ' + str(ACCEPTANCE_AFFECT_BY),
    )

    @classmethod
    def create_final_acceptance_indicators(
            cls,
            list_indicator,
    ):
        cls.objects.bulk_create(list_indicator)
        return True

    class Meta:
        verbose_name = 'Final Acceptance Indicator'
        verbose_name_plural = 'Final Acceptance Indicators'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()
