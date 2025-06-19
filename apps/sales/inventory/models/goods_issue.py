from django.db import models
from django.db import transaction

from apps.core.attachments.models import M2MFilesAbstractModel
from apps.masterdata.saledata.models import ProductWareHouseLot, SubPeriods, ProductWareHouseSerial, ProductWareHouse
from apps.sales.report.utils.log_for_goods_issue import IRForGoodsIssueHandler
from apps.shared import DataAbstractModel, SimpleAbstractModel, GOODS_ISSUE_TYPE, AutoDocumentAbstractModel

__all__ = ['GoodsIssue', 'GoodsIssueProduct']


class GoodsIssue(DataAbstractModel, AutoDocumentAbstractModel):
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
    work_order = models.ForeignKey(
        'production.WorkOrder',
        on_delete=models.CASCADE,
        related_name='goods_issue_wo',
        null=True,
    )
    product_modification = models.ForeignKey(
        'productmodification.ProductModification',
        on_delete=models.CASCADE,
        related_name='goods_issue_pm',
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
                sn_list = ProductWareHouseSerial.objects.filter(id__in=data.sn_data, serial_status=0)
                if len(data.sn_data) == sn_list.count():
                    sn_list.update(serial_status=1)
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
    def update_issued_quantity_production_order_item(cls, po_item_obj, this_issue_quantity):
        po_item_obj.issued_quantity += this_issue_quantity
        po_item_obj.save(update_fields=['issued_quantity'])
        return True

    @classmethod
    def update_issued_quantity_work_order_item(cls, wo_item_obj, this_issue_quantity):
        wo_item_obj.issued_quantity += this_issue_quantity
        wo_item_obj.save(update_fields=['issued_quantity'])
        return True

    @classmethod
    def update_related_app_after_issue(cls, instance):
        try:
            with transaction.atomic():
                if instance.inventory_adjustment:
                    for item in instance.goods_issue_product.all():
                        cls.update_product_warehouse_data(item)
                        cls.update_status_inventory_adjustment_item(
                            item.inventory_adjustment_item, item.issued_quantity
                        )
                elif instance.production_order:
                    for item in instance.goods_issue_product.all():
                        cls.update_product_warehouse_data(item)
                        cls.update_issued_quantity_production_order_item(
                            item.production_order_item, item.issued_quantity
                        )
                elif instance.work_order:
                    for item in instance.goods_issue_product.all():
                        cls.update_product_warehouse_data(item)
                        cls.update_issued_quantity_work_order_item(
                            item.work_order_item, item.issued_quantity
                        )
                elif instance.product_modification:
                    for item in instance.goods_issue_product.all():
                        cls.update_product_warehouse_data(item)
                return True
        except Exception as err:
            print(err)
            raise err

    def save(self, *args, **kwargs):
        if not kwargs.pop('skip_check_period', False):
            SubPeriods.check_period(self.tenant_id, self.company_id)

        if self.system_status in [2, 3]:
            if not self.code:
                self.add_auto_generate_code_to_instance(self, 'GI[n4]', True)

                if 'update_fields' in kwargs:
                    if isinstance(kwargs['update_fields'], list):
                        kwargs['update_fields'].append('code')
                else:
                    kwargs.update({'update_fields': ['code']})

                self.update_related_app_after_issue(self)

                IRForGoodsIssueHandler.push_to_inventory_report(self)

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
    work_order_item = models.ForeignKey(
        'production.WorkOrderTask',
        on_delete=models.CASCADE,
        related_name='wo_item_goods_issue',
        null=True,
    )
    product_modification_item = models.ForeignKey(
        'productmodification.CurrentComponent',
        on_delete=models.CASCADE,
        related_name='pm_item_goods_issue',
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


class GoodsIssueAttachmentFile(M2MFilesAbstractModel):
    goods_issue = models.ForeignKey(
        GoodsIssue,
        on_delete=models.CASCADE,
        related_name='goods_issue_attachments'
    )

    @classmethod
    def get_doc_field_name(cls):
        return 'goods_issue'

    class Meta:
        verbose_name = 'Goods issue attachment'
        verbose_name_plural = 'Goods issue attachments'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
