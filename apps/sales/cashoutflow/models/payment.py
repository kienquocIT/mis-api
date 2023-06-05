from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.shared import DataAbstractModel, SimpleAbstractModel
from .advance_payment import AdvancePaymentCost

__all__ = ['Payment', 'PaymentCost', 'PaymentCostItems', 'PaymentCostItemsDetail']

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
    sale_code_mapped = models.JSONField(
        default=list
    )
    sale_code_type = models.SmallIntegerField(
        choices=SALE_CODE_TYPE,
        help_text='0 is Sale, 1 is Purchase, 2 is None-sale, 3 is Others'
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
    beneficiary = models.ForeignKey(
        'hr.Employee',
        on_delete=models.CASCADE,
        related_name='payment_beneficiary'
    )

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
    expense = models.ForeignKey(
        'saledata.Expense',
        on_delete=models.CASCADE,
    )
    expense_unit_of_measure = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE
    )
    expense_quantity = models.IntegerField()
    expense_unit_price = models.FloatField(default=0)
    tax = models.ForeignKey(
        'saledata.Tax',
        null=True,
        on_delete=models.CASCADE
    )
    tax_price = models.FloatField(default=0)
    subtotal_price = models.FloatField(default=0)
    after_tax_price = models.FloatField(default=0)
    currency = models.ForeignKey(
        'saledata.Currency',
        on_delete=models.CASCADE
    )
    document_number = models.CharField(
        max_length=150
    )
    expense_ap_detail_list = models.JSONField(default=list)
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


class PaymentCostItems(SimpleAbstractModel):
    payment_cost = models.ForeignKey(
        PaymentCost,
        on_delete=models.CASCADE,
        related_name='payment_cost'
    )
    sale_code_mapped = models.UUIDField(null=True)
    real_value = models.FloatField(default=0, help_text='Value which is NOT CONVERTED from Advance Payment')
    converted_value = models.FloatField(default=0, help_text='Value which is CONVERTED from Advance Payment')
    sum_value = models.FloatField(default=0, help_text='Sum value (include real_value and value_converted')
    expense_items_detail_list = models.JSONField(default=list)
    date_created = models.DateTimeField(
        default=timezone.now,
        editable=False,
        help_text='The record created at value'
    )

    class Meta:
        verbose_name = 'Payment Cost Items'
        verbose_name_plural = 'Payment Costs Items'
        ordering = ('date_created',)
        default_permissions = ()
        permissions = ()


class PaymentCostItemsDetail(SimpleAbstractModel):
    payment_cost_item = models.ForeignKey(
        PaymentCostItems,
        on_delete=models.CASCADE,
        related_name='payment_cost_item'
    )
    payment_mapped = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
    )
    expense_converted = models.ForeignKey(
        AdvancePaymentCost,
        on_delete=models.CASCADE,
        related_name='expense_converted',
        null=True
    )
    expense_value_converted = models.FloatField(
        default=0,
        help_text='Value which is CONVERTED from Advance Payment Expense'
    )
    date_created = models.DateTimeField(
        default=timezone.now,
        editable=False,
        help_text='The record created at value'
    )

    class Meta:
        verbose_name = 'Payment Cost Item Detail'
        verbose_name_plural = 'Payment Cost Item Details'
        ordering = ('date_created',)
        default_permissions = ()
        permissions = ()
