from django.db import models

from apps.core.company.models import CompanyFunctionNumber
from apps.sales.inventory.utils.logical_finish_recovery import RecoveryFinishHandler
from apps.shared import DataAbstractModel, STATUS_RECOVERY, MasterDataAbstractModel, ASSET_TYPE


class GoodsRecovery(DataAbstractModel):
    customer = models.ForeignKey(
        'saledata.Account',
        on_delete=models.CASCADE,
        verbose_name="customer",
        related_name="goods_recovery_customer",
        null=True,
    )
    customer_data = models.JSONField(default=dict, help_text='data json of customer')
    lease_order = models.ForeignKey(
        'leaseorder.LeaseOrder',
        on_delete=models.CASCADE,
        verbose_name="lease order",
        related_name="goods_recovery_lease",
        null=True,
    )
    lease_order_data = models.JSONField(default=dict, help_text='data json of lease order')
    date_recovery = models.DateField(verbose_name="date recovery", null=True)
    status_recovery = models.SmallIntegerField(default=0, help_text='choices= ' + str(STATUS_RECOVERY))
    remark = models.TextField(verbose_name='remark', blank=True, null=True)
    recovery_delivery_data = models.JSONField(default=list, help_text='data json of recovery deliveries')
    # total
    total_pretax = models.FloatField(default=0)
    total_tax = models.FloatField(default=0)
    total = models.FloatField(default=0)
    total_revenue_before_tax = models.FloatField(default=0)

    class Meta:
        verbose_name = 'Goods Recovery'
        verbose_name_plural = 'Goods Recoveries'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    def save(self, *args, **kwargs):
        if self.system_status in [2, 3] and 'update_fields' in kwargs:  # added, finish
            # check if date_approved then call related functions
            if isinstance(kwargs['update_fields'], list):
                if 'date_approved' in kwargs['update_fields']:
                    CompanyFunctionNumber.auto_gen_code_based_on_config('goodsrecovery', True, self, kwargs)
                    RecoveryFinishHandler.run_logics(instance=self)

        # hit DB
        super().save(*args, **kwargs)


class RecoveryDelivery(MasterDataAbstractModel):  # relation: 1GoodsRecovery-*RecoveryDelivery
    goods_recovery = models.ForeignKey(
        GoodsRecovery,
        on_delete=models.CASCADE,
        verbose_name="goods recovery",
        related_name="recovery_delivery_recovery",
    )
    delivery = models.ForeignKey(
        'delivery.OrderDeliverySub',
        on_delete=models.CASCADE,
        verbose_name="delivery",
        related_name="recovery_delivery_delivery",
    )
    delivery_data = models.JSONField(default=dict, help_text='data json of delivery')
    delivery_product_data = models.JSONField(default=list, help_text='data json of delivery products')

    class Meta:
        verbose_name = 'Recovery Delivery'
        verbose_name_plural = 'Recovery Deliveries'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class RecoveryProduct(MasterDataAbstractModel):  # relation: 1RecoveryDelivery-*RecoveryProduct
    goods_recovery = models.ForeignKey(
        GoodsRecovery,
        on_delete=models.CASCADE,
        verbose_name="goods recovery",
        related_name="recovery_product_recovery",
    )
    recovery_delivery = models.ForeignKey(
        RecoveryDelivery,
        on_delete=models.CASCADE,
        verbose_name="recovery delivery",
        related_name="recovery_product_rd",
    )
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        verbose_name="product",
        related_name="recovery_product_product",
    )
    product_data = models.JSONField(default=dict, help_text='data json of product')
    asset_type = models.SmallIntegerField(null=True, help_text='choices= ' + str(ASSET_TYPE))
    offset = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        verbose_name="offset",
        related_name="recovery_product_offset",
        null=True
    )
    offset_data = models.JSONField(default=dict, help_text='data json of offset')
    asset_data = models.JSONField(default=list, help_text='data json of asset')
    tool_data = models.JSONField(default=list, help_text='data json of tool')
    uom = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        verbose_name='uom',
        related_name="recovery_product_uom",
        null=True
    )
    uom_data = models.JSONField(default=dict, help_text='data json of uom')
    uom_time = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        verbose_name='uom',
        related_name="recovery_product_uom_time",
        null=True,
    )
    uom_time_data = models.JSONField(default=dict, help_text='data json of uom time')
    product_quantity = models.FloatField(default=0)
    product_quantity_time = models.FloatField(default=0)
    product_cost = models.FloatField(default=0)
    product_subtotal_cost = models.FloatField(default=0)
    quantity_recovery = models.FloatField(default=0)
    delivery_data = models.JSONField(default=list, help_text='data json of product delivery')

    # Begin depreciation fields

    product_depreciation_subtotal = models.FloatField(default=0)
    product_depreciation_price = models.FloatField(default=0)
    product_depreciation_method = models.SmallIntegerField(default=0)  # (0: 'Line', 1: 'Adjustment')
    product_depreciation_adjustment = models.FloatField(default=0)
    product_depreciation_time = models.FloatField(default=0)
    product_depreciation_start_date = models.DateField(null=True)
    product_depreciation_end_date = models.DateField(null=True)

    product_lease_start_date = models.DateField(null=True)
    product_lease_end_date = models.DateField(null=True)

    depreciation_data = models.JSONField(default=list, help_text='data json of depreciation')
    depreciation_lease_data = models.JSONField(default=list, help_text='data json of depreciation lease')

    # End depreciation fields

    class Meta:
        verbose_name = 'Recovery Product'
        verbose_name_plural = 'Recovery Products'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class RecoveryProductTool(MasterDataAbstractModel):
    goods_recovery = models.ForeignKey(
        GoodsRecovery,
        on_delete=models.CASCADE,
        verbose_name="goods recovery",
        related_name="recovery_product_tool_recovery",
    )
    recovery_product = models.ForeignKey(
        RecoveryProduct,
        on_delete=models.CASCADE,
        verbose_name="recovery product",
        related_name="recovery_product_tool_recovery_product",
    )
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        verbose_name="product",
        related_name="recovery_product_tool_product",
        null=True
    )
    product_data = models.JSONField(default=dict, help_text='data json of product')
    tool = models.ForeignKey(
        'asset.InstrumentTool',
        on_delete=models.CASCADE,
        verbose_name="tool",
        related_name="recovery_product_tool_tool",
        null=True
    )
    tool_data = models.JSONField(default=dict, help_text='data json of tool')
    uom_time = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        verbose_name="uom time",
        related_name="recovery_product_tool_uom_time",
        null=True
    )
    uom_time_data = models.JSONField(default=dict, help_text='data json of uom time')
    product_quantity = models.FloatField(default=0)
    product_quantity_time = models.FloatField(default=0)
    quantity_recovery = models.FloatField(default=0)
    # Begin depreciation fields

    product_depreciation_subtotal = models.FloatField(default=0)
    product_depreciation_price = models.FloatField(default=0)
    product_depreciation_method = models.SmallIntegerField(default=0)  # (0: 'Line', 1: 'Adjustment')
    product_depreciation_adjustment = models.FloatField(default=0)
    product_depreciation_time = models.FloatField(default=0)
    product_depreciation_start_date = models.DateField(null=True)
    product_depreciation_end_date = models.DateField(null=True)

    product_lease_start_date = models.DateField(null=True)
    product_lease_end_date = models.DateField(null=True)

    depreciation_data = models.JSONField(default=list, help_text='data json of depreciation')
    depreciation_lease_data = models.JSONField(default=list, help_text='data json of depreciation lease')

    # End depreciation fields

    # fields for recovery
    quantity_remain_recovery = models.FloatField(default=0, help_text="minus when recovery")

    class Meta:
        verbose_name = 'Recovery Product Tool'
        verbose_name_plural = 'Recovery Products Tools'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class RecoveryProductAsset(MasterDataAbstractModel):
    goods_recovery = models.ForeignKey(
        GoodsRecovery,
        on_delete=models.CASCADE,
        verbose_name="goods recovery",
        related_name="recovery_product_asset_recovery",
    )
    recovery_product = models.ForeignKey(
        RecoveryProduct,
        on_delete=models.CASCADE,
        verbose_name="recovery product",
        related_name="recovery_product_asset_recovery_product",
    )
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        verbose_name="product",
        related_name="recovery_product_asset_product",
        null=True
    )
    product_data = models.JSONField(default=dict, help_text='data json of product')
    asset = models.ForeignKey(
        'asset.FixedAsset',
        on_delete=models.CASCADE,
        verbose_name="asset",
        related_name="recovery_product_asset_asset",
        null=True
    )
    asset_data = models.JSONField(default=dict, help_text='data json of asset')
    uom_time = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        verbose_name="uom time",
        related_name="recovery_product_asset_uom_time",
        null=True
    )
    uom_time_data = models.JSONField(default=dict, help_text='data json of uom time')
    product_quantity = models.FloatField(default=0)
    product_quantity_time = models.FloatField(default=0)
    quantity_recovery = models.FloatField(default=0)
    # Begin depreciation fields

    product_depreciation_subtotal = models.FloatField(default=0)
    product_depreciation_price = models.FloatField(default=0)
    product_depreciation_method = models.SmallIntegerField(default=0)  # (0: 'Line', 1: 'Adjustment')
    product_depreciation_adjustment = models.FloatField(default=0)
    product_depreciation_time = models.FloatField(default=0)
    product_depreciation_start_date = models.DateField(null=True)
    product_depreciation_end_date = models.DateField(null=True)

    product_lease_start_date = models.DateField(null=True)
    product_lease_end_date = models.DateField(null=True)

    depreciation_data = models.JSONField(default=list, help_text='data json of depreciation')
    depreciation_lease_data = models.JSONField(default=list, help_text='data json of depreciation lease')

    # End depreciation fields

    # fields for recovery
    quantity_remain_recovery = models.FloatField(default=0, help_text="minus when recovery")

    class Meta:
        verbose_name = 'Recovery Product Asset'
        verbose_name_plural = 'Recovery Products Asset'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
