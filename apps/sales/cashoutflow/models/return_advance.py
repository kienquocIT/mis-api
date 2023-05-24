from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.shared import DataAbstractModel, SimpleAbstractModel

__all__ = ['ReturnAdvance', 'ReturnAdvanceCost']

RETURN_ADVANCE_METHOD = [
    (0, _('Cash')),
    (1, _('Bank Transfer')),
]


class ReturnAdvance(DataAbstractModel):
    advance_payment = models.ForeignKey(
        'cashoutflow.AdvancePayment',
        on_delete=models.CASCADE,
        related_name='advance_payment'

    )
    method = models.SmallIntegerField(
        choices=RETURN_ADVANCE_METHOD,
        verbose_name='AdvancePayment method',
        help_text='0 is Cash, 1 is Bank Transfer',
        default=0
    )
    creator = models.ForeignKey(
        'hr.Employee',
        on_delete=models.CASCADE,
        related_name='creator_name'
    )
    beneficiary = models.ForeignKey(
        'hr.Employee',
        on_delete=models.CASCADE,
        related_name='beneficiary'
    )
    money_received = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Return Advance'
        verbose_name_plural = 'Return Advances'
        ordering = ('date_created',)
        default_permissions = ()
        permissions = ()


class ReturnAdvanceCost(SimpleAbstractModel):
    return_advance = models.ForeignKey(
        ReturnAdvance,
        on_delete=models.CASCADE,
        related_name='return_advance'
    )
    expense = models.ForeignKey(
        'saledata.Expense',
        on_delete=models.CASCADE,
        related_name='return_advance_expense'
    )
    remain_total = models.FloatField(
        default=0,
    )
    return_price = models.FloatField(
        default=0,
    )
