from django.db import models
from apps.accounting.accountingsettings.models.account_masterdata_models import DEFAULT_ACCOUNT_DETERMINATION_TYPE
from apps.shared import MasterDataAbstractModel, SimpleAbstractModel

__all__ = [
    'WarehouseAccountDetermination',
    'WarehouseAccountDeterminationSub'
]


class WarehouseAccountDetermination(MasterDataAbstractModel):
    warehouse_mapped = models.ForeignKey(
        'saledata.WareHouse',
        on_delete=models.CASCADE,
        related_name='wh_account_deter_warehouse_mapped'
    )
    account_number_list = models.JSONField(default=list)
    # [{'id', 'acc_code', 'acc_name', 'foreign_acc_name', 'default_account_determination_type'}]
    account_determination_type = models.SmallIntegerField(choices=DEFAULT_ACCOUNT_DETERMINATION_TYPE, default=0)
    is_change = models.BooleanField(default=False, help_text='True if user has change default account determination')

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
    wh_account_deter_warehouse = models.ForeignKey(
        'saledata.WareHouse',
        on_delete=models.CASCADE,
        related_name='wh_account_deter_subs_warehouse'
    )
    account_mapped = models.ForeignKey(
        'accountingsettings.ChartOfAccounts',
        on_delete=models.CASCADE,
        related_name='wh_account_deter_subs_account_mapped'
    )

    class Meta:
        verbose_name = 'Warehouse Account Determination Sub'
        verbose_name_plural = 'Warehouse Account Determination Sub'
        ordering = ()
        default_permissions = ()
        permissions = ()
