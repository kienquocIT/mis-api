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
    'PaymentOpportunity',
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
    expense_ap_detail_list = models.JSONField(default=list)

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


class PaymentCostItems(SimpleAbstractModel):
    payment_cost = models.ForeignKey(
        PaymentCost,
        on_delete=models.CASCADE,
        related_name='payment_cost'
    )
    sale_code_mapped = models.UUIDField(null=True)
    sale_code_mapped_code = models.CharField(max_length=150, null=True)
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
        related_name='product_converted',
        null=True
    )
    expense_value_converted = models.FloatField(
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
