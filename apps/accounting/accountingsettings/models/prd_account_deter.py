from django.db import models
from apps.accounting.accountingsettings.models.account_masterdata_models import DEFAULT_ACCOUNT_DETERMINATION_TYPE
from apps.shared import MasterDataAbstractModel, SimpleAbstractModel

__all__ = [
    'ProductAccountDetermination',
]


class ProductAccountDetermination(MasterDataAbstractModel):
    product_mapped = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        related_name='prd_account_deter_product_mapped'
    )
    account_number_list = models.JSONField(default=list)  # [111, 222, 333, 444]

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
        related_name='prd_account_deter_subs'
    )
    account_mapped = models.ForeignKey(
        'accountingsettings.ChartOfAccounts',
        on_delete=models.CASCADE,
        related_name='prd_account_deter_account_mapped'
    )
    account_determination_type = models.SmallIntegerField(choices=DEFAULT_ACCOUNT_DETERMINATION_TYPE, default=0)
    is_change = models.BooleanField(default=False, help_text='True if user has change default account determination')

    class Meta:
        verbose_name = 'Product Account Determination Sub'
        verbose_name_plural = 'Product Account Determination Sub'
        ordering = ()
        default_permissions = ()
        permissions = ()
