from django.db import models
from django.db import transaction
from apps.masterdata.saledata.models import ProductWareHouseLot, SubPeriods, ProductWareHouseSerial, ProductWareHouse
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
    production_order = models.ForeignKey(
        'production.ProductionOrder',
        on_delete=models.CASCADE,
        related_name='goods_issue_po',
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
                    if prd_wh_lot and lot_item.get('quantity', 0) > 0:
                        casted_quantity = ReportStockLog.cast_quantity_to_unit(item.uom, lot_item.get('quantity', 0))
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
                                'lot_quantity': lot_item.get('quantity', 0),
                                'lot_value': 0,  # theo gia cost,
                                'lot_expire_date': str(prd_wh_lot.expire_date) if prd_wh_lot.expire_date else None
                            }
                        })
            else:
                casted_quantity = ReportStockLog.cast_quantity_to_unit(item.uom, item.issued_quantity)
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
        product_warehouse = ProductWareHouse.objects.filter(product=data.product, warehouse=data.warehouse).first()
        if product_warehouse and product_warehouse.stock_amount - data.issued_quantity >= 0:
            if data.product.general_traceability_method == 0:
                product_warehouse.sold_amount += data.issued_quantity
                product_warehouse.stock_amount = product_warehouse.receipt_amount - product_warehouse.sold_amount
                product_warehouse.save(update_fields=['sold_amount', 'stock_amount'])
            elif data.product.general_traceability_method == 1:
                sum_lot_issue = 0
                for lot in data.lot_data:
                    if float(lot.get('quantity', 0)) > 0:
                        lot_obj = ProductWareHouseLot.objects.filter(id=lot.get('lot_id')).first()
                        if lot_obj and lot_obj.quantity_import >= float(lot.get('quantity', 0)):
                            sum_lot_issue += float(lot.get('quantity', 0))
                            lot_obj.quantity_import -= float(lot.get('quantity', 0))
                            lot_obj.save(update_fields=['quantity_import'])
                        else:
                            raise ValueError('Issued quantity cannot > lot stock quantity.')
                product_warehouse.sold_amount += sum_lot_issue
                product_warehouse.stock_amount = product_warehouse.receipt_amount - product_warehouse.sold_amount
                product_warehouse.save(update_fields=['sold_amount', 'stock_amount'])
            elif data.product.general_traceability_method == 2:
                sn_list = ProductWareHouseSerial.objects.filter(id__in=data.sn_data, is_delete=False)
                if len(data.sn_data) == sn_list.count():
                    sn_list.update(is_delete=True)
                    product_warehouse.sold_amount += len(data.sn_data)
                    product_warehouse.stock_amount = product_warehouse.receipt_amount - product_warehouse.sold_amount
                    product_warehouse.save(update_fields=['sold_amount', 'stock_amount'])
                else:
                    raise ValueError('Some serials selected for issued have not existed already.')
            return True
        raise ValueError('Stock quantity cannot < 0.')

    @classmethod
    def update_status_inventory_adjustment_item(cls, ia_item_obj, this_issue_quantity):
        if ia_item_obj.book_quantity - ia_item_obj.count - ia_item_obj.issued_quantity - this_issue_quantity >= 0:
            ia_item_obj.action_status = (
                ia_item_obj.book_quantity - ia_item_obj.count - ia_item_obj.issued_quantity - this_issue_quantity
            ) == 0
            ia_item_obj.select_for_action = True
            ia_item_obj.issued_quantity += this_issue_quantity
            ia_item_obj.save(update_fields=['action_status', 'select_for_action', 'issued_quantity'])
            return True
        raise ValueError('Issued quantity cannot > max issue quantity remaining.')

    @classmethod
    def update_status_production_order_item(cls, po_item_obj, this_issue_quantity):
        if po_item_obj.quantity - po_item_obj.issued_quantity - this_issue_quantity >= 0:
            po_item_obj.issued_quantity += this_issue_quantity
            po_item_obj.save(update_fields=['issued_quantity'])
            return True
        raise ValueError('Issued quantity cannot > max issue quantity remaining.')

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
                temper = "%04d" % (goods_issue + 1)  # pylint: disable=C0209
                self.code = f"GI{temper}"

                if 'update_fields' in kwargs:
                    if isinstance(kwargs['update_fields'], list):
                        kwargs['update_fields'].append('code')
                else:
                    kwargs.update({'update_fields': ['code']})

                self.prepare_data_for_logging(self)

                if self.inventory_adjustment:
                    try:
                        with transaction.atomic():
                            for item in self.goods_issue_product.all():
                                self.update_product_warehouse_data(item)
                                self.update_status_inventory_adjustment_item(
                                    item.inventory_adjustment_item, item.issued_quantity
                                )
                            self.inventory_adjustment.update_ia_state()
                    except Exception as err:
                        print(err)
                        raise err
                elif self.production_order:
                    try:
                        with transaction.atomic():
                            for item in self.goods_issue_product.all():
                                self.update_product_warehouse_data(item)
                                self.update_status_production_order_item(
                                    item.production_order_item, item.issued_quantity
                                )
                            self.production_order.update_production_order_issue_state()
                    except Exception as err:
                        print(err)
                        raise err

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
    production_order_item = models.ForeignKey(
        'production.ProductionOrderTask',
        on_delete=models.CASCADE,
        related_name='po_item_goods_issue',
        null=True,
    )
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        related_name='product_goods_issue',
    )
    product_data = models.JSONField(default=dict)
    warehouse = models.ForeignKey(
        'saledata.WareHouse',
        on_delete=models.CASCADE,
        related_name='warehouse_goods_issue',
    )
    warehouse_data = models.JSONField(default=dict)
    uom = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        related_name='uom_goods_issue',
    )
    uom_data = models.JSONField(default=dict)

    before_quantity = models.FloatField(default=0)
    remain_quantity = models.FloatField(default=0)
    issued_quantity = models.FloatField(default=0)
    lot_data = models.JSONField(default=list)  # [{'lot_id': ..., 'old_quantity': ..., 'quantity': ...}]
    sn_data = models.JSONField(default=list)  # [..., ..., ...]

    class Meta:
        verbose_name = 'Goods Issue Product'
        verbose_name_plural = 'Goods Issue Products'
        ordering = ('product__code',)
        default_permissions = ()
        permissions = ()
