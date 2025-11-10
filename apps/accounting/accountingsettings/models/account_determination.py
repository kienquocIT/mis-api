from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.shared import MasterDataAbstractModel, SimpleAbstractModel


__all__ = [
    'AccountDetermination',
    'AccountDeterminationSub'
]


ACCOUNT_DETERMINATION_TYPE = [
    (0, _('Sale')),
    (1, _('Purchasing')),
    (2, _('Inventory')),
    (3, _('Fixed, Assets')),
]


class AccountDetermination(MasterDataAbstractModel):
    order = models.IntegerField(default=0)
    foreign_title = models.CharField(max_length=100, blank=True)
    account_determination_type = models.SmallIntegerField(choices=ACCOUNT_DETERMINATION_TYPE, default=0)
    can_change_account = models.BooleanField(default=False)
    is_changed = models.BooleanField(default=False, help_text='True if user has change default account determination')

    @classmethod
    def get_account_determination_sub_data(cls, tenant_id, company_id, foreign_title):
        account_deter = AccountDetermination.objects.filter(
            tenant_id=tenant_id, company_id=company_id, foreign_title=foreign_title
        ).first()
        return [item.account_mapped for item in account_deter.account_determination_sub.all()] if account_deter else []

    class Meta:
        verbose_name = 'Account Determination'
        verbose_name_plural = 'Account Determination'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


class AccountDeterminationSub(SimpleAbstractModel):
    account_determination = models.ForeignKey(
        AccountDetermination,
        on_delete=models.CASCADE,
        related_name='account_determination_sub'
    )
    account_mapped = models.ForeignKey(
        'accountingsettings.ChartOfAccounts',
        on_delete=models.CASCADE,
        related_name='account_determination_account_mapped'
    )
    account_mapped_data = models.JSONField(default=dict)
    # {'id', 'acc_code', 'acc_name', 'foreign_acc_name'}

    class Meta:
        verbose_name = 'Account Determination Sub'
        verbose_name_plural = 'Account Determination Sub'
        ordering = ()
        default_permissions = ()
        permissions = ()
