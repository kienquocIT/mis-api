from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.company.models import CompanyFunctionNumber
from apps.shared import DataAbstractModel, SimpleAbstractModel
from .advance_payment import AdvancePaymentCost


__all__ = ['ReturnAdvance', 'ReturnAdvanceCost']

from ..utils import ReturnAdHandler

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
    return_total = models.FloatField(default=0)
    money_received = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Return Advance'
        verbose_name_plural = 'Return Advances'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    @classmethod
    def update_advance_payment_cost(cls, instance):
        # instance.money_received = True
        # instance.save(update_fields=['money_received'])
        if instance.money_received:
            for item in instance.return_advance.all():
                item.advance_payment_cost.sum_return_value += item.return_value
                item.advance_payment_cost.save(update_fields=['sum_return_value'])
            return True
        return False

    def save(self, *args, **kwargs):
        if self.system_status in [2, 3]:
            if not self.code:
                code_generated = CompanyFunctionNumber.gen_code(company_obj=self.company, func=8)
                if code_generated:
                    self.code = code_generated
                else:
                    records = ReturnAdvance.objects.filter(
                        company=self.company, tenant=self.tenant, is_delete=False, system_status=3
                    )
                    self.code = 'RP.00' + str(records.count() + 1)

                if 'update_fields' in kwargs:
                    if isinstance(kwargs['update_fields'], list):
                        kwargs['update_fields'].append('code')
                else:
                    kwargs.update({'update_fields': ['code']})
                self.update_advance_payment_cost(self)

        # opportunity log
        ReturnAdHandler.push_opportunity_log(instance=self)
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
