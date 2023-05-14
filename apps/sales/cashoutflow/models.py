from django.db import models
from apps.shared import DataAbstractModel

__all__ = ['AdvancePayment']


class AdvancePayment(DataAbstractModel):
    sale_code = models.ForeignKey('opportunity.Opportunity', on_delete=models.CASCADE, null=True)
    sale_code_type = models.SmallIntegerField(help_text='0 is Sale, 1 is Purchase')
    type = models.BooleanField(help_text='0 is For Employee, 1 is For Supplier', default=False)
    supplier = models.UUIDField(verbose_name='Supplier mapped', null=True)
    method = models.SmallIntegerField(verbose_name='AdvancePayment method', help_text='0 is Cash, 1 is Bank Transfer')
    creator_name = models.ForeignKey('hr.Employee', on_delete=models.CASCADE, related_name='advance_creator_name')
    beneficiary = models.ForeignKey('hr.Employee', on_delete=models.CASCADE, related_name='advance_beneficiary')
    return_date = models.DateTimeField()

    class Meta:
        verbose_name = 'AdvancePayment'
        verbose_name_plural = 'AdvancesPayments'
        ordering = ('date_created',)
        default_permissions = ()
        permissions = ()
