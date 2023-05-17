from django.db import models
from django.utils import timezone
from apps.shared import DataAbstractModel, SimpleAbstractModel

__all__ = ['AdvancePayment', 'AdvancePaymentCost']


class AdvancePayment(DataAbstractModel):
    sale_code = models.ForeignKey('opportunity.Opportunity', on_delete=models.CASCADE, null=True)
    sale_code_type = models.SmallIntegerField(help_text='0 is Sale, 1 is Purchase')
    type = models.BooleanField(help_text='0 is For Employee, 1 is For Supplier', default=False)
    supplier = models.UUIDField(verbose_name='Supplier mapped', null=True)
    method = models.SmallIntegerField(verbose_name='AdvancePayment method', help_text='0 is Cash, 1 is Bank Transfer')
    creator_name = models.ForeignKey('hr.Employee', on_delete=models.CASCADE, related_name='advance_creator_name')
    beneficiary = models.ForeignKey('hr.Employee', on_delete=models.CASCADE, related_name='advance_beneficiary')
    return_date = models.DateTimeField()
    money_gave = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Advance Payment'
        verbose_name_plural = 'Advances Payments'
        ordering = ('date_created',)
        default_permissions = ()
        permissions = ()


class AdvancePaymentCost(SimpleAbstractModel):
    advance_payment = models.ForeignKey(AdvancePayment, on_delete=models.CASCADE)
    expense = models.ForeignKey('saledata.Expense', on_delete=models.CASCADE)
    expense_unit_of_measure = models.ForeignKey('saledata.UnitOfMeasure', on_delete=models.CASCADE)
    expense_quantity = models.IntegerField()
    expense_unit_price = models.FloatField(default=0)
    tax = models.ForeignKey('saledata.Tax', null=True, on_delete=models.CASCADE)
    tax_price = models.FloatField(default=0)
    subtotal_price = models.FloatField(default=0)
    after_tax_price = models.FloatField(default=0)
    currency = models.ForeignKey('saledata.Currency', on_delete=models.CASCADE)
    date_created = models.DateTimeField(default=timezone.now, editable=False, help_text='The record created at value')

    class Meta:
        verbose_name = 'Advance Payment Cost'
        verbose_name_plural = 'Advance Payment Costs'
        ordering = ('date_created',)
        default_permissions = ()
        permissions = ()
