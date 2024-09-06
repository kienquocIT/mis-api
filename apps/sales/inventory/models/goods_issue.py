import json
from django.db import models
from apps.masterdata.saledata.models import ProductWareHouseLot, SubPeriods
from apps.sales.report.models import ReportStockLog
from apps.shared import DataAbstractModel, SimpleAbstractModel, GOODS_ISSUE_TYPE

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
        blank=True,
        null=True
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
            if len(item.lot_data) > 0:
                for lot_item in item.lot_data:
                    prd_wh_lot = ProductWareHouseLot.objects.filter(id=lot_item['lot_id']).first()
                    quantity = lot_item['old_quantity'] - lot_item['quantity']
                    if prd_wh_lot and quantity > 0:
                        casted_quantity = ReportStockLog.cast_quantity_to_unit(item.uom, quantity)
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
                            'quantity': casted_quantity,
                            'cost': 0,  # theo gia cost
                            'value': 0,  # theo gia cost
                            'lot_data': {
                                'lot_id': str(prd_wh_lot.id),
                                'lot_number': prd_wh_lot.lot_number,
                                'lot_quantity': quantity,
                                'lot_value': item.unit_cost * quantity,
                                'lot_expire_date': str(prd_wh_lot.expire_date) if prd_wh_lot.expire_date else None
                            }
                        })
            else:
                casted_quantity = ReportStockLog.cast_quantity_to_unit(item.uom, item.quantity)
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
                    'quantity': casted_quantity,
                    'cost': 0,  # theo gia cost
                    'value': 0,  # theo gia cost
                    'lot_data': {}
                })
        ReportStockLog.logging_inventory_activities(
            instance,
            instance.date_approved,
            activities_data
        )
        return True

    @classmethod
    def update_product_warehouse_data(cls, data):
        pass
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
        SubPeriods.check_open(
            self.company_id,
            self.tenant_id,
            self.date_approved if self.date_approved else self.date_created
        )

        if self.system_status in [2, 3]:
            if not self.code:
                goods_issue = GoodsIssue.objects.filter_current(
                    fill__tenant=True, fill__company=True, is_delete=False, system_status=3
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
                    for item in self.goods_issue_product.all():
                        self.update_product_warehouse_data(item)
                        self.update_status_inventory_adjustment_item(
                            self.inventory_adjustment,
                            item.get('inventory_adjustment_item'),
                        )
                    self.inventory_adjustment.update_ia_state()

        super().save(*args, **kwargs)


class GoodsIssueProduct(SimpleAbstractModel):
    goods_issue = models.ForeignKey(
        GoodsIssue,
        on_delete=models.CASCADE,
        related_name='goods_issue_product'
    )
    inventory_adjustment_item = models.ForeignKey(
        'inventory.InventoryAdjustmentItem',
        on_delete=models.CASCADE,
        related_name='ia_item_goods_issue',
        null=True,
    )
    product_warehouse = models.ForeignKey(
        'saledata.ProductWareHouse',
        on_delete=models.CASCADE,
        related_name='product_warehouse_goods_issue',
    )
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        related_name='product_goods_issue',
    )
    warehouse = models.ForeignKey(
        'saledata.WareHouse',
        on_delete=models.CASCADE,
        related_name='warehouse_goods_issue',
    )
    uom = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        related_name='uom_goods_issue',
    )
    lot_data = models.JSONField(default=list)  # [{'lot_id': ..., 'old_quantity': ..., 'quantity': ...}]
    sn_data = models.JSONField(default=list)  # [..., ..., ...]
    limit_quantity = models.FloatField(default=0)
    quantity = models.FloatField(default=0)

    class Meta:
        verbose_name = 'Goods Issue Product'
        verbose_name_plural = 'Goods Issue Products'
        ordering = ('product__code',)
        default_permissions = ()
        permissions = ()
