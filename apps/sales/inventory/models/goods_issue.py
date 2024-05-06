import json
from django.db import models
from apps.masterdata.saledata.models import ProductWareHouseLot, ProductWareHouse
from apps.sales.report.models import ReportInventorySub
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
                    'lot_changes': [],
                    'sn_changes': []
                }
            ]
        )
    )

    class Meta:
        verbose_name = 'Goods Issue'
        verbose_name_plural = 'Goods Issue'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    @classmethod
    def prepare_data_for_logging(cls, instance):
        activities_data = []
        for item in instance.goods_issue_product.all():
            lot_data = []
            for lot_item in item.lot_data:
                prd_wh_lot = ProductWareHouseLot.objects.filter(id=lot_item['lot_id']).first()
                quantity = lot_item['old_quantity'] - lot_item['quantity']
                if prd_wh_lot and quantity > 0:
                    lot_data.append({
                        'lot_id': str(prd_wh_lot.id),
                        'lot_number': prd_wh_lot.lot_number,
                        'lot_quantity': quantity,
                        'lot_value': item.unit_cost * quantity,
                        'lot_expire_date': str(prd_wh_lot.expire_date)
                    })
            activities_data.append({
                'product': item.product,
                'warehouse': item.warehouse,
                'system_date': instance.date_approved,
                'posting_date': instance.date_approved,
                'document_date': instance.date_approved,
                'stock_type': -1,
                'trans_id': str(instance.id),
                'trans_code': instance.code,
                'trans_title': 'Goods issue',
                'quantity': item.quantity,
                'cost': item.unit_cost,
                'value': item.unit_cost * item.quantity,
                'lot_data': lot_data
            })
        ReportInventorySub.logging_when_stock_activities_happened(
            instance,
            instance.date_approved,
            activities_data
        )
        return True

    @classmethod
    def update_product_amount(cls, data):
        ProductWareHouse.pop_from_transfer(
            product_warehouse_id=data['product_warehouse']['id'],
            amount=data['quantity'],
            data=data
        )
        return True

    @classmethod
    def update_status_inventory_adjustment_item(cls, ia_obj, ia_item_id):
        item = ia_obj.inventory_adjustment_item_mapped.filter(id=ia_item_id).first()
        if item:
            item.action_status = True
            item.select_for_action = True
            item.save(update_fields=['action_status', 'select_for_action'])
        return True

    def save(self, *args, **kwargs):
        if self.system_status in [2, 3]:
            if not self.code:
                goods_issue = GoodsIssue.objects.filter_current(
                    fill__tenant=True, fill__company=True, is_delete=False
                ).count()
                char = "GI"
                temper = "%04d" % (goods_issue + 1)  # pylint: disable=C0209
                code = f"{char}{temper}"
                self.code = code

                if 'update_fields' in kwargs:
                    if isinstance(kwargs['update_fields'], list):
                        kwargs['update_fields'].append('code')
                else:
                    kwargs.update({'update_fields': ['code']})

                self.prepare_data_for_logging(self)
                if self.inventory_adjustment:
                    for item in self.goods_issue_datas:
                        self.update_product_amount(item)
                        self.update_status_inventory_adjustment_item(
                            self.inventory_adjustment,
                            item.get('inventory_adjustment_item'),
                        )
                    self.inventory_adjustment.update_ia_state()

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
