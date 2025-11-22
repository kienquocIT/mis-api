from django.db import models
from apps.accounting.accountingsettings.models.account_determination import ACCOUNT_DETERMINATION_TYPE
from apps.shared import MasterDataAbstractModel, SimpleAbstractModel


__all__ = [
    'ProductAccountDetermination',
    'ProductAccountDeterminationSub'
]


class ProductAccountDetermination(MasterDataAbstractModel):
    foreign_title = models.CharField(max_length=100, blank=True)
    product_mapped = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        related_name='prd_account_deter_product_mapped'
    )
    account_determination_type = models.SmallIntegerField(choices=ACCOUNT_DETERMINATION_TYPE, default=0)
    can_change_account = models.BooleanField(default=False, help_text='True if user can change')

    class Meta:
        verbose_name = 'Product Account Determination'
        verbose_name_plural = 'Product Account Determination'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class ProductAccountDeterminationSub(SimpleAbstractModel):
    prd_account_deter = models.ForeignKey(
        ProductAccountDetermination,
        on_delete=models.CASCADE,
        related_name='prd_account_deter_sub'
    )
    account_mapped = models.ForeignKey(
        'accountingsettings.ChartOfAccounts',
        on_delete=models.CASCADE,
        related_name='prd_account_deter_account_mapped'
    )
    account_mapped_data = models.JSONField(default=dict)
    # {'id', 'acc_code', 'acc_name', 'foreign_acc_name'}

    class Meta:
        verbose_name = 'Product Account Determination Sub'
        verbose_name_plural = 'Product Account Determination Sub'
        ordering = ()
        default_permissions = ()
        permissions = ()
