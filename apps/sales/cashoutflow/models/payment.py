from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.shared import DataAbstractModel, SimpleAbstractModel
from .advance_payment import AdvancePaymentCost

__all__ = [
    'Payment',
    'PaymentCost',
    'PaymentConfig'
]

SALE_CODE_TYPE = [
    (0, _('Sale')),
    (1, _('Purchase')),
    (2, _('None-sale')),
    (3, _('Others'))
]

ADVANCE_PAYMENT_METHOD = [
    (0, _('Cash')),
    (1, _('Bank Transfer')),
]


class Payment(DataAbstractModel):
    sale_order_mapped = models.ForeignKey(
        'saleorder.SaleOrder',
        on_delete=models.CASCADE, null=True,
        related_name="payment_sale_order_mapped"
    )
    quotation_mapped = models.ForeignKey(
        'quotation.Quotation',
        on_delete=models.CASCADE, null=True,
        related_name="payment_quotation_mapped"
    )
    opportunity_mapped = models.ForeignKey(
        'opportunity.Opportunity',
        on_delete=models.CASCADE, null=True,
        related_name="payment_opportunity_mapped"
    )
    sale_code_type = models.SmallIntegerField(
        choices=SALE_CODE_TYPE,
        help_text='0 is Sale, 1 is Purchase, 2 is None-sale'
    )
    supplier = models.ForeignKey(
        'saledata.Account',
        verbose_name='Supplier mapped',
        on_delete=models.CASCADE,
    )
    method = models.SmallIntegerField(
        choices=ADVANCE_PAYMENT_METHOD,
        verbose_name='Payment method',
        help_text='0 is Cash, 1 is Bank Transfer'
    )
    creator_name = models.ForeignKey(
        'hr.Employee',
        on_delete=models.CASCADE,
        related_name='payment_creator_name'
    )
    status = models.BooleanField(default=0)

    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class PaymentCost(SimpleAbstractModel):
    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name='payment'
    )
    expense_type = models.ForeignKey('saledata.ExpenseItem', on_delete=models.CASCADE, null=True)
    expense_description = models.CharField(max_length=150, null=True)
    expense_uom_name = models.CharField(max_length=150, null=True)
    expense_quantity = models.IntegerField()
    expense_unit_price = models.FloatField(default=0)
    expense_tax = models.ForeignKey('saledata.Tax', null=True, on_delete=models.CASCADE)
    expense_tax_price = models.FloatField(default=0)
    expense_subtotal_price = models.FloatField(default=0)
    expense_after_tax_price = models.FloatField(default=0)
    document_number = models.CharField(max_length=150)
    real_value = models.FloatField(default=0)
    converted_value = models.FloatField(default=0)
    sum_value = models.FloatField(default=0)
    ap_cost_converted_list = models.JSONField(default=list)

    currency = models.ForeignKey('saledata.Currency', on_delete=models.CASCADE)

    date_created = models.DateTimeField(
        default=timezone.now,
        editable=False,
        help_text='The record created at value'
    )

    class Meta:
        verbose_name = 'Payment Cost'
        verbose_name_plural = 'Payment Costs'
        ordering = ('date_created',)
        default_permissions = ()
        permissions = ()


class PaymentConfig(SimpleAbstractModel):
    company = models.ForeignKey(
        'company.Company',
        on_delete=models.CASCADE,
    )
    employee_allowed = models.ForeignKey('hr.Employee', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Payment Config'
        verbose_name_plural = 'Payment Configs'
        default_permissions = ()
        permissions = ()
