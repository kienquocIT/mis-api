from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.attachments.models import M2MFilesAbstractModel
from apps.core.company.models import CompanyFunctionNumber
from apps.shared import DataAbstractModel, SimpleAbstractModel, MasterDataAbstractModel

__all__ = ['AccountingAccount']

ACC_TYPE = [
    (0, _("Off-table accounts")),
    (1, _("Assets")),
    (2, _("Liabilities")),
    (3, _("Owner's equity")),
    (4, _("Revenue")),
    (5, _("Costs of production, business")),
    (6, _("Other incomes")),
    (7, _("Other expenses")),
    (8, _("Income summary")),
]


class AccountingAccount(MasterDataAbstractModel):
    order = models.IntegerField(default=0)
    acc_code = models.CharField(max_length=100)
    acc_name = models.CharField(max_length=100)
    foreign_acc_name = models.CharField(max_length=100)
    acc_status = models.BooleanField(default=True)
    acc_type = models.SmallIntegerField(choices=ACC_TYPE)
    parent_account = models.ForeignKey('self', on_delete=models.CASCADE, null=True)
    level = models.IntegerField(default=1)
    is_account = models.BooleanField(default=True)
    control_account = models.BooleanField(default=False)
    is_all_currency = models.BooleanField(default=True)
    currency_mapped = models.ForeignKey('saledata.Currency', on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = 'Main Account'
        verbose_name_plural = 'Main Accounts'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
