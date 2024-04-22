import json
from django.db import models
from apps.shared import DataAbstractModel, MasterDataAbstractModel, GOODS_ISSUE_TYPE

__all__ = ['GoodsIssue', 'GoodsIssueProduct']


class GoodsIssue(DataAbstractModel):
    goods_issue_type = models.SmallIntegerField(
        default=0,
        choices=GOODS_ISSUE_TYPE,
        help_text='choices= ' + str(GOODS_ISSUE_TYPE),
    )
    inventory_adjustment = models.ForeignKey(
        'inventory.InventoryAdjustment',
        on_delete=models.CASCADE,
        related_name='goods_issue_ia',
        null=True,
    )
    note = models.CharField(
        max_length=1000,
        default='',
        blank=True,
    )
    date_issue = models.DateTimeField()
    goods_issue_datas = models.JSONField(
        help_text=json.dumps(
            [
                {
                    'warehouse': {
                        'id': 'warehouse_id',
                        'title': 'warehouse_title',
                    },
                    'product': {  # product in warehouse
                        'id': 'id',
                        'product_data': {
                            'id': 'product_id',
                            'title': 'product_title',
                        }
                    },
                    'uom': {
                        'id': 'uom_id',
                        'title': 'uom_title'
                    },
                    'quantity': 2,
                    'product_warehouse_id': 'product_warehouse_id',
                    'inventory_adjustment_item_id': 'inventory_adjustment_item_id',
                    'description': 'xxx',
                    'unit_cost': 500000,
                    'subtotal_cost': 1000000,
                }
            ]
        )
    )

    class Meta:
        verbose_name = 'Goods Transfer'
        verbose_name_plural = 'Goods Transfer'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    def save(self, *args, **kwargs):
        # auto create code (temporary)
        goods_issue = GoodsIssue.objects.filter_current(
            fill__tenant=True,
            fill__company=True,
            is_delete=False
        ).count()
        char = "GI"
        if not self.code:
            temper = "%04d" % (goods_issue + 1)  # pylint: disable=C0209
            code = f"{char}{temper}"
            self.code = code
        # hit DB
        super().save(*args, **kwargs)


class GoodsIssueProduct(MasterDataAbstractModel):
    goods_issue = models.ForeignKey(
        GoodsIssue,
        on_delete=models.CASCADE,
        related_name='goods_issue_product'
    )
    product_warehouse = models.ForeignKey(
        'saledata.ProductWareHouse',
        on_delete=models.CASCADE,
        related_name='product_warehouse_goods_issue',
    )
    inventory_adjustment_item = models.ForeignKey(
        'inventory.InventoryAdjustmentItem',
        on_delete=models.CASCADE,
        related_name='ia_item_goods_issue',
        null=True,
    )
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        related_name='product_goods_issue',
    )
    product_title = models.CharField(
        max_length=500,
    )
    uom = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        related_name='uom_goods_issue',
    )
    uom_title = models.CharField(
        max_length=500,
    )
    warehouse = models.ForeignKey(
        'saledata.WareHouse',
        on_delete=models.CASCADE,
        related_name='warehouse_goods_issue',
    )
    warehouse_title = models.CharField(
        max_length=500,
    )
    description = models.CharField(
        max_length=1000,
        blank=True
    )
    lot_data = models.JSONField(default=list)  # [{'lot_id': ..., 'old_quantity': ..., 'quantity': ...}]
    sn_data = models.JSONField(default=list)  # [..., ..., ...]
    quantity = models.FloatField()
    unit_cost = models.FloatField()
    subtotal = models.FloatField()

    class Meta:
        verbose_name = 'Goods Issue Product'
        verbose_name_plural = 'Goods Issue Products'
        ordering = ()
        default_permissions = ()
        permissions = ()
