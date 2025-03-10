from django.db import models

from apps.sales.inventory.utils.logical_finish_recovery import RecoveryFinishHandler
# from apps.sales.inventory.utils.logical_finish_recovery import RecoveryFinishHandler
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

    @classmethod
    def find_max_number(cls, codes):
        num_max = None
        for code in codes:
            try:
                if code != '':
                    tmp = int(code.split('-', maxsplit=1)[0].split("GR")[1])
                    if num_max is None or (isinstance(num_max, int) and tmp > num_max):
                        num_max = tmp
            except Exception as err:
                print(err)
        return num_max

    @classmethod
    def generate_code(cls, company_id):
        existing_codes = cls.objects.filter(company_id=company_id).values_list('code', flat=True)
        num_max = cls.find_max_number(existing_codes)
        if num_max is None:
            code = 'GR0001'
        elif num_max < 10000:
            num_str = str(num_max + 1).zfill(4)
            code = f'GR{num_str}'
        else:
            raise ValueError('Out of range: number exceeds 10000')
        if cls.objects.filter(code=code, company_id=company_id).exists():
            return cls.generate_code(company_id=company_id)
        return code

    @classmethod
    def push_code(cls, instance, kwargs):
        if not instance.code:
            instance.code = cls.generate_code(company_id=instance.company_id)
            kwargs['update_fields'].append('code')
        return True

    def save(self, *args, **kwargs):
        if self.system_status in [2, 3] and 'update_fields' in kwargs:  # added, finish
            # check if date_approved then call related functions
            if isinstance(kwargs['update_fields'], list):
                if 'date_approved' in kwargs['update_fields']:
                    # code
                    self.push_code(instance=self, kwargs=kwargs)
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
    uom = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        verbose_name='uom',
        related_name="recovery_product_uom",
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
    product_warehouse_data = models.JSONField(default=list, help_text='data json of product warehouses')

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

    # End depreciation fields

    class Meta:
        verbose_name = 'Recovery Product'
        verbose_name_plural = 'Recovery Products'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class RecoveryWarehouse(MasterDataAbstractModel):  # relation: 1RecoveryProduct-*RecoveryWarehouse
    goods_recovery = models.ForeignKey(
        GoodsRecovery,
        on_delete=models.CASCADE,
        verbose_name="goods recovery",
        related_name="recovery_warehouse_recovery",
    )
    recovery_product = models.ForeignKey(
        RecoveryProduct,
        on_delete=models.CASCADE,
        verbose_name="recovery product",
        related_name="recovery_warehouse_rp",
    )
    warehouse = models.ForeignKey(
        'saledata.WareHouse',
        on_delete=models.CASCADE,
        verbose_name="product",
        related_name="recovery_warehouse_warehouse",
    )
    warehouse_data = models.JSONField(default=dict, help_text='data json of warehouse')
    quantity_recovery = models.FloatField(default=0)

    lease_generate_data = models.JSONField(default=list, help_text='data json of product warehouses')

    class Meta:
        verbose_name = 'Recovery warehouse'
        verbose_name_plural = 'Recovery warehouses'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class RecoveryLeaseGenerate(MasterDataAbstractModel):  # relation: 1RecoveryProduct-*RecoveryWarehouse
    goods_recovery = models.ForeignKey(
        GoodsRecovery,
        on_delete=models.CASCADE,
        verbose_name="goods recovery",
        related_name="recovery_lease_generate_recovery",
    )
    recovery_warehouse = models.ForeignKey(
        RecoveryWarehouse,
        on_delete=models.CASCADE,
        verbose_name="recovery warehouse",
        related_name="recovery_lease_generate_rw",
    )
    serial = models.ForeignKey(
        'saledata.ProductWareHouseSerial',
        on_delete=models.CASCADE,
        verbose_name="serial",
        related_name="recovery_lease_generate_serial",
        null=True,
    )
    serial_data = models.JSONField(default=dict, help_text='data json of serial')
    remark = models.TextField(verbose_name='remark', blank=True, null=True)

    class Meta:
        verbose_name = 'Recovery lease generate'
        verbose_name_plural = 'Recovery lease generates'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
