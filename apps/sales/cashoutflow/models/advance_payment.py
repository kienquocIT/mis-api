from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.shared import DataAbstractModel, SimpleAbstractModel

__all__ = ['AdvancePayment', 'AdvancePaymentCost']

SALE_CODE_TYPE = [
    (0, _('Sale')),
    (1, _('Purchase')),
    (2, _('None-sale'))
]

ADVANCE_PAYMENT_TYPE = [
    (0, _('For Employee')),
    (1, _('For Supplier')),
]

ADVANCE_PAYMENT_METHOD = [
    (0, _('Cash')),
    (1, _('Bank Transfer')),
]


class AdvancePayment(DataAbstractModel):
    sale_order_mapped = models.ForeignKey(
        'saleorder.SaleOrder',
        on_delete=models.CASCADE, null=True,
        related_name="ap_sale_order_mapped"
    )
    quotation_mapped = models.ForeignKey(
        'quotation.Quotation',
        on_delete=models.CASCADE, null=True,
        related_name="ap_quotation_mapped"
    )
    opportunity_mapped = models.ForeignKey(
        'opportunity.Opportunity',
        on_delete=models.CASCADE, null=True,
        related_name="ap_opportunity_mapped"
    )
    sale_code_type = models.SmallIntegerField(
        choices=SALE_CODE_TYPE,
        help_text='0 is Sale, 1 is Purchase, 2 is None-sale'
    )
    advance_payment_type = models.SmallIntegerField(
        choices=ADVANCE_PAYMENT_TYPE,
        verbose_name='AdvancePayment type',
        help_text='0 is For Employee, 1 is For Supplier',
        default=False
    )
    supplier = models.ForeignKey(
        'saledata.Account',
        verbose_name='Supplier mapped',
        on_delete=models.CASCADE,
        null=True
    )
    method = models.SmallIntegerField(
        choices=ADVANCE_PAYMENT_METHOD,
        verbose_name='AdvancePayment method',
        help_text='0 is Cash, 1 is Bank Transfer'
    )
    creator_name = models.ForeignKey(
        'hr.Employee',
        on_delete=models.CASCADE,
        related_name='advance_creator_name'
    )
    return_date = models.DateTimeField()
    money_gave = models.BooleanField(default=False)
    status = models.BooleanField(default=0)

    class Meta:
        verbose_name = 'Advance Payment'
        verbose_name_plural = 'Advances Payments'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    def save(self, *args, **kwargs):
        if not self.code:
            function_number = self.company.company_function_number.filter(function=6).first()
            if function_number:
                self.code = function_number.gen_code(company_obj=self.company, func=6)
            if not self.code:
                records = AdvancePayment.objects.filter_current(fill__tenant=True, fill__company=True, is_delete=False)
                self.code = 'AP.00' + str(records.count() + 1)
        super().save(*args, **kwargs)


class AdvancePaymentCost(SimpleAbstractModel):
    advance_payment = models.ForeignKey(AdvancePayment, on_delete=models.CASCADE, related_name='advance_payment')
    sale_order_mapped = models.ForeignKey(
        'saleorder.SaleOrder',
        on_delete=models.CASCADE, null=True,
        related_name="ap_cost_sale_order_mapped"
    )
    quotation_mapped = models.ForeignKey(
        'quotation.Quotation',
        on_delete=models.CASCADE, null=True,
        related_name="ap_cost_quotation_mapped"
    )
    opportunity_mapped = models.ForeignKey(
        'opportunity.Opportunity',
        on_delete=models.CASCADE, null=True,
        related_name="ap_cost_opportunity_mapped"
    )
    expense_name = models.CharField(max_length=150, null=True)
    expense_type = models.ForeignKey('saledata.ExpenseItem', on_delete=models.CASCADE, null=True)
    expense_uom_name = models.CharField(max_length=150, null=True)
    expense_quantity = models.IntegerField()
    expense_unit_price = models.FloatField(default=0)
    expense_tax = models.ForeignKey('saledata.Tax', null=True, on_delete=models.CASCADE)
    expense_tax_price = models.FloatField(default=0)
    expense_subtotal_price = models.FloatField(default=0)
    expense_after_tax_price = models.FloatField(default=0)

    sum_return_value = models.FloatField(default=0)
    sum_converted_value = models.FloatField(default=0)
    sum_real_value = models.FloatField(default=0)

    currency = models.ForeignKey('saledata.Currency', on_delete=models.CASCADE)
    date_created = models.DateTimeField(
        default=timezone.now,
        editable=False,
        help_text='The record created at value'
    )

    class Meta:
        verbose_name = 'Advance Payment Cost'
        verbose_name_plural = 'Advance Payment Costs'
        ordering = ('date_created',)
        default_permissions = ()
        permissions = ()
