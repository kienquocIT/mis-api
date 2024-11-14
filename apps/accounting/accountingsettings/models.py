from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.attachments.models import M2MFilesAbstractModel
from apps.core.company.models import CompanyFunctionNumber
from apps.shared import DataAbstractModel, SimpleAbstractModel, MasterDataAbstractModel

__all__ = ['ChartOfAccounts']

CHART_OF_ACCOUNT_TYPE = [
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

DEFAULT_ACCOUNT_DEFINITION_TYPE = [
    (0, _('Sale')),
    (1, _('Purchasing')),
    (2, _('Inventory')),
]


class ChartOfAccounts(MasterDataAbstractModel):
    order = models.IntegerField(default=0)
    acc_code = models.CharField(max_length=100)
    acc_name = models.CharField(max_length=100)
    foreign_acc_name = models.CharField(max_length=100)
    acc_status = models.BooleanField(default=True)
    acc_type = models.SmallIntegerField(choices=CHART_OF_ACCOUNT_TYPE)
    parent_account = models.ForeignKey('self', on_delete=models.CASCADE, null=True)
    has_child = models.BooleanField(default=False)
    level = models.IntegerField(default=1)
    is_account = models.BooleanField(default=True)
    control_account = models.BooleanField(default=False)
    is_all_currency = models.BooleanField(default=True)
    currency_mapped = models.ForeignKey('saledata.Currency', on_delete=models.CASCADE, null=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Chart Of Accounts'
        verbose_name_plural = 'Chart Of Accounts'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class DefaultAccountDefinition(MasterDataAbstractModel):
    account_mapped = models.ForeignKey(ChartOfAccounts, on_delete=models.CASCADE)
    type = models.SmallIntegerField(choices=DEFAULT_ACCOUNT_DEFINITION_TYPE, default=0)
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Default Account Definition'
        verbose_name_plural = 'Default Account Definition'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
