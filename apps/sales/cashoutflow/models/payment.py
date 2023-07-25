from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.shared import DataAbstractModel, SimpleAbstractModel
from .advance_payment import AdvancePaymentCost

__all__ = [
    'Payment',
    'PaymentCost',
    'PaymentCostItems',
    'PaymentCostItemsDetail',
    'PaymentSaleOrder',
    'PaymentQuotation',
    'PaymentOpportunity'
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
    sale_order_mapped = models.ManyToManyField(
        'saleorder.SaleOrder',
        through='PaymentSaleOrder',
        symmetrical=False,
        blank=True,
        related_name='sale_order_mapped'
    )
    quotation_mapped = models.ManyToManyField(
        'quotation.Quotation',
        through='PaymentQuotation',
        symmetrical=False,
        blank=True,
        related_name='quotation_mapped'
    )
    opportunity_mapped = models.ManyToManyField(
        'opportunity.Opportunity',
        through='PaymentOpportunity',
        symmetrical=False,
        blank=True,
        related_name='opportunity_mapped'
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
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        null=True
    )
    product_unit_of_measure = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE
    )
    product_quantity = models.IntegerField()
    product_unit_price = models.FloatField(default=0)
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
    product_ap_detail_list = models.JSONField(default=list)
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
    product_items_detail_list = models.JSONField(default=list)
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
    product_converted = models.ForeignKey(
        AdvancePaymentCost,
        on_delete=models.CASCADE,
        related_name='product_converted',
        null=True
    )
    product_value_converted = models.FloatField(
        default=0,
        help_text='Value which is CONVERTED from Advance Payment product'
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


class PaymentSaleOrder(SimpleAbstractModel):
    payment_mapped = models.ForeignKey(Payment, on_delete=models.CASCADE)
    sale_order_mapped = models.ForeignKey('saleorder.SaleOrder', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Payment Sale Order'
        verbose_name_plural = 'Payments Sale Orders'
        default_permissions = ()
        permissions = ()


class PaymentQuotation(SimpleAbstractModel):
    payment_mapped = models.ForeignKey(Payment, on_delete=models.CASCADE)
    quotation_mapped = models.ForeignKey('quotation.Quotation', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Payment Quotation'
        verbose_name_plural = 'Payments Quotations'
        default_permissions = ()
        permissions = ()


class PaymentOpportunity(SimpleAbstractModel):
    payment_mapped = models.ForeignKey(Payment, on_delete=models.CASCADE)
    opportunity_mapped = models.ForeignKey('opportunity.Opportunity', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Payment Opportunity'
        verbose_name_plural = 'Payments Opportunities'
        default_permissions = ()
        permissions = ()
