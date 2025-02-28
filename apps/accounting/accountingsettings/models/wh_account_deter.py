from django.db import models
from apps.accounting.accountingsettings.models.account_masterdata_models import DEFAULT_ACCOUNT_DETERMINATION_TYPE
from apps.shared import MasterDataAbstractModel, SimpleAbstractModel

__all__ = [
    'WarehouseAccountDetermination',
]


class WarehouseAccountDetermination(MasterDataAbstractModel):
    warehouse_mapped = models.ForeignKey(
        'saledata.WareHouse',
        on_delete=models.CASCADE,
        related_name='wh_account_deter_warehouse_mapped'
    )
    account_number_list = models.JSONField(default=list)  # [111, 222, 333, 444]

    class Meta:
        verbose_name = 'Warehouse Account Determination'
        verbose_name_plural = 'Warehouse Account Determination'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class WarehouseAccountDeterminationSub(SimpleAbstractModel):
    wh_account_deter = models.ForeignKey(
        WarehouseAccountDetermination,
        on_delete=models.CASCADE,
        related_name='wh_account_deter_subs'
    )
    account_mapped = models.ForeignKey(
        'accountingsettings.ChartOfAccounts',
        on_delete=models.CASCADE,
        related_name='wh_account_deter_subs_account_mapped'
    )
    account_determination_type = models.SmallIntegerField(choices=DEFAULT_ACCOUNT_DETERMINATION_TYPE, default=0)
    is_change = models.BooleanField(default=False, help_text='True if user has change default account determination')

    class Meta:
        verbose_name = 'Warehouse Account Determination Sub'
        verbose_name_plural = 'Warehouse Account Determination Sub'
        ordering = ()
        default_permissions = ()
        permissions = ()
