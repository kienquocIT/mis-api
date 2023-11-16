from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.shared import DataAbstractModel, SimpleAbstractModel, RETURN_ADVANCE_STATUS
from .advance_payment import AdvancePaymentCost


__all__ = ['ReturnAdvance', 'ReturnAdvanceCost']

RETURN_ADVANCE_METHOD = [
    (0, _('Cash')),
    (1, _('Bank Transfer')),
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
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    def save(self, *args, **kwargs):
        if not self.code:
            function_number = self.company.company_function_number.filter(function=8).first()
            if function_number:
                self.code = function_number.gen_code(company_obj=self.company, func=8)
            else:
                records = ReturnAdvance.objects.filter_current(fill__tenant=True, fill__company=True, is_delete=False)
                self.code = 'RP.00' + str(records.count() + 1)
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
    expense_type = models.ForeignKey(
        'saledata.ExpenseItem',
        on_delete=models.CASCADE,
        null=True,
        related_name='return_advance_expense'
    )
    expense_name = models.CharField(
        max_length=150,
        null=True
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
