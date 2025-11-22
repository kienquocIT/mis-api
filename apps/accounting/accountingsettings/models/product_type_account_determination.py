from django.db import models
from apps.accounting.accountingsettings.models.account_determination import ACCOUNT_DETERMINATION_TYPE
from apps.shared import MasterDataAbstractModel, SimpleAbstractModel


__all__ = [
    'ProductTypeAccountDetermination',
    'ProductTypeAccountDeterminationSub'
]


class ProductTypeAccountDetermination(MasterDataAbstractModel):
    foreign_title = models.CharField(max_length=100, blank=True)
    product_type_mapped = models.ForeignKey(
        'saledata.ProductType',
        on_delete=models.CASCADE,
        related_name='prd_type_account_deter_product_type_mapped'
    )
    account_determination_type = models.SmallIntegerField(choices=ACCOUNT_DETERMINATION_TYPE, default=0)
    can_change_account = models.BooleanField(default=False, help_text='True if user can change')

    class Meta:
        verbose_name = 'Product Type Account Determination'
        verbose_name_plural = 'Product Type Account Determination'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class ProductTypeAccountDeterminationSub(SimpleAbstractModel):
    prd_type_account_deter = models.ForeignKey(
        ProductTypeAccountDetermination,
        on_delete=models.CASCADE,
        related_name='prd_type_account_deter_sub'
    )
    account_mapped = models.ForeignKey(
        'accountingsettings.ChartOfAccounts',
        on_delete=models.CASCADE,
        related_name='prd_type_account_deter_account_mapped'
    )
    account_mapped_data = models.JSONField(default=dict)
    # {'id', 'acc_code', 'acc_name', 'foreign_acc_name'}

    class Meta:
        verbose_name = 'Product Type Account Determination Sub'
        verbose_name_plural = 'Product Type Account Determination Sub'
        ordering = ()
        default_permissions = ()
        permissions = ()
