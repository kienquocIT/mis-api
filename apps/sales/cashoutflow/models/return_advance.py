from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.sales.cashoutflow.models import AdvancePaymentCost
from apps.shared import DataAbstractModel, SimpleAbstractModel

__all__ = ['ReturnAdvance', 'ReturnAdvanceCost']

RETURN_ADVANCE_METHOD = [
    (0, _('Cash')),
    (1, _('Bank Transfer')),
]
RETURN_ADVANCE_STATUS = [
    (0, _('Approved')),
]


class ReturnAdvance(DataAbstractModel):
    advance_payment = models.ForeignKey(
        'cashoutflow.AdvancePayment',
        on_delete=models.CASCADE,
        related_name='return_advance_payment'

    )
    method = models.SmallIntegerField(
        choices=RETURN_ADVANCE_METHOD,
        verbose_name='method return',
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
    status = models.SmallIntegerField(
        choices=RETURN_ADVANCE_STATUS,
        verbose_name='status of Return Advance',
        default=0
    )
    return_total = models.FloatField(
        default=0
    )
    money_received = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Return Advance'
        verbose_name_plural = 'Return Advances'
        ordering = ('date_created',)
        default_permissions = ()
        permissions = ()

    def save(self, *args, **kwargs):
        return_advance = ReturnAdvance.objects.filter_current(
            fill__tenant=True,
            fill__company=True,
            is_delete=False
        ).count()
        char = "RA.CODE."
        if not self.code:
            temper = "%04d" % (return_advance + 1)  # pylint: disable=C0209
            code = f"{char}{temper}"
            self.code = code

        # hit DB
        super().save(*args, **kwargs)


class ReturnAdvanceCost(SimpleAbstractModel):
    return_advance = models.ForeignKey(
        ReturnAdvance,
        on_delete=models.CASCADE,
        related_name='return_advance'
    )
    advance_payment_cost = models.ForeignKey(
        AdvancePaymentCost,
        on_delete=models.CASCADE,
        null=True,
        related_name='advance_payment_cost',
    )
    remain_value = models.FloatField(
        default=0,
    )
    return_value = models.FloatField(
        default=0,
    )

    class Meta:
        verbose_name = 'Return Advance Cost'
        verbose_name_plural = 'Return Advance Costs'
        default_permissions = ()
        permissions = ()
