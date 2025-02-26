from django.db import models
from apps.accounting.accountingsettings.models.account_masterdata_models import DEFAULT_ACCOUNT_DETERMINATION_TYPE
from apps.shared import MasterDataAbstractModel

__all__ = [
    'ProductTypeAccountDetermination',
]


class ProductTypeAccountDetermination(MasterDataAbstractModel):
    product_type_mapped = models.ForeignKey(
        'saledata.ProductType',
        on_delete=models.CASCADE,
        related_name='prd_type_account_deter_product_type_mapped'
    )
    account_mapped = models.ForeignKey(
        'accountingsettings.ChartOfAccounts',
        on_delete=models.CASCADE,
        related_name='prd_type_account_deter_account_mapped'
    )
    account_determination_type = models.SmallIntegerField(choices=DEFAULT_ACCOUNT_DETERMINATION_TYPE, default=0)
    is_change = models.BooleanField(default=False, help_text='True if user has change default account determination')

    class Meta:
        verbose_name = 'Product Type Account Determination'
        verbose_name_plural = 'Product Type Account Determination'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
