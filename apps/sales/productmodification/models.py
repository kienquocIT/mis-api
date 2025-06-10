from django.db import models

from apps.sales.inventory.models import GoodsIssue, GoodsIssueProduct
from apps.sales.report.utils import IRForGoodsIssueHandler
from apps.shared import SimpleAbstractModel, DataAbstractModel


class ProductModification(DataAbstractModel):
    product_modified = models.ForeignKey('saledata.Product', on_delete=models.CASCADE, related_name='product_modified')
    prd_wh = models.ForeignKey('saledata.ProductWareHouse', on_delete=models.CASCADE, null=True)
    prd_wh_data = models.JSONField(default=dict)

    prd_wh_lot = models.ForeignKey('saledata.ProductWareHouseLot', on_delete=models.CASCADE, null=True)
    prd_wh_lot_data = models.JSONField(default=dict)

    prd_wh_serial = models.ForeignKey('saledata.ProductWareHouseSerial', on_delete=models.CASCADE, null=True)
    prd_wh_serial_data = models.JSONField(default=dict)

    @classmethod
    def prepare_data_for_goods_issue(cls, pm_obj):
        detail_data = []
        for item in pm_obj.current_components.all():
            try:
                uom = item.component_product.general_uom_group.uom_reference
            except AttributeError:
                uom = None
            for child in item.current_components_detail.all():
                if child.component_prd_wh:
                    try:
                        warehouse = child.component_prd_wh.warehouse
                    except AttributeError:
                        warehouse = None
                    detail_data.append({
                        'product_modification_item': item,
                        'product': item.component_product,
                        'product_data': item.component_product_data,
                        'warehouse': warehouse,
                        'warehouse_data': {
                            'id': str(warehouse.id), 'code': warehouse.code, 'title': warehouse.title,
                        } if warehouse else {},
                        'uom': uom,
                        'uom_data': {
                            'id': str(uom.id), 'code': uom.code, 'title': uom.title,
                        } if uom else {},
                        'before_quantity': child.component_prd_wh_quantity,
                        'remain_quantity': child.component_prd_wh_quantity,
                        'issued_quantity': child.component_prd_wh_quantity,
                        'lot_data': [],
                        'sn_data': []
                    })
                if child.component_prd_wh_lot:
                    try:
                        warehouse = child.component_prd_wh_lot.product_warehouse.warehouse
                    except AttributeError:
                        warehouse = None
                    detail_data.append({
                        'product_modification_item': item,
                        'product': item.component_product,
                        'product_data': item.component_product_data,
                        'warehouse': warehouse,
                        'warehouse_data': {
                            'id': str(warehouse.id), 'code': warehouse.code, 'title': warehouse.title,
                        } if warehouse else {},
                        'uom': uom,
                        'uom_data': {
                            'id': str(uom.id), 'code': uom.code, 'title': uom.title,
                        } if uom else {},
                        'before_quantity': child.component_prd_wh_lot_quantity,
                        'remain_quantity': child.component_prd_wh_lot_quantity,
                        'issued_quantity': child.component_prd_wh_lot_quantity,
                        'lot_data': [{
                            'lot_id': str(child.component_prd_wh_lot_id),
                            'old_quantity': child.component_prd_wh_lot.quantity_import,
                            'quantity': child.component_prd_wh_lot_quantity
                        }],
                        'sn_data': []
                    })
                if child.component_prd_wh_serial:
                    try:
                        warehouse = child.component_prd_wh_serial.product_warehouse.warehouse
                    except AttributeError:
                        warehouse = None
                    detail_data.append({
                        'product_modification_item': item,
                        'product': item.component_product,
                        'product_data': item.component_product_data,
                        'warehouse': warehouse,
                        'warehouse_data': {
                            'id': str(warehouse.id), 'code': warehouse.code, 'title': warehouse.title,
                        } if warehouse else {},
                        'uom': uom,
                        'uom_data': {
                            'id': str(uom.id), 'code': uom.code, 'title': uom.title,
                        } if uom else {},
                        'before_quantity': 1,
                        'remain_quantity': 1,
                        'issued_quantity': 1,
                        'lot_data': [],
                        'sn_data': [str(child.component_prd_wh_serial_id)]
                    })
        gis_data = {
            'title': f'Goods issue for {pm_obj.code}',
            'goods_issue_type': 3,
            'product_modification': pm_obj,
            'system_auto_create': True,
            'tenant': pm_obj.tenant,
            'company': pm_obj.company,
            'employee_created': pm_obj.employee_created,
            'employee_inherit': pm_obj.employee_inherit,
            'date_created': pm_obj.date_created,
            'date_approved': pm_obj.date_approved,
            'detail_data': detail_data
        }
        return gis_data

    @classmethod
    def auto_create_goods_issue(cls, pm_obj):
        """
        Phiếu Xuất kho được tạo từ chức năng này sẽ tự động duyệt mà không quan tâm quy trình như thế nào
        """
        gis_data = cls.prepare_data_for_goods_issue(pm_obj)
        detail_data = gis_data.pop('detail_data', [])
        gis_obj = GoodsIssue.objects.create(**gis_data)
        bulk_info = []
        for item in detail_data:
            bulk_info.append(GoodsIssueProduct(goods_issue=gis_obj, **item))
        GoodsIssueProduct.objects.filter(goods_issue=gis_obj).delete()
        GoodsIssueProduct.objects.bulk_create(bulk_info)

        # duyệt tự động
        gis_obj.add_auto_generate_code_to_instance(gis_obj, 'GI[n4]', True)
        gis_obj.system_status = 3
        gis_obj.save(update_fields=['code', 'system_status'])
        # action sau khi duyệt
        if pm_obj.prd_wh:
            pm_obj.prd_wh.sold_amount += 1
            pm_obj.prd_wh.stock_amount = pm_obj.prd_wh.receipt_amount - 1
            pm_obj.prd_wh.save(update_fields=['sold_amount', 'stock_amount'])

        if pm_obj.prd_wh_serial_id:
            pm_obj.prd_wh_serial.serial_status = 1
            pm_obj.prd_wh_serial.save(update_fields=['serial_status'])

        if pm_obj.prd_wh_lot_id:
            pm_obj.prd_wh_lot.quantity_import -= 1
            pm_obj.prd_wh_lot.save(update_fields=['quantity_import'])

        gis_obj.update_related_app_after_issue(gis_obj)
        IRForGoodsIssueHandler.push_to_inventory_report(gis_obj)

        return True

    def save(self, *args, **kwargs):
        if self.system_status in [2, 3]:
            if not self.code:
                self.add_auto_generate_code_to_instance(self, 'PRD-MOD-[n4]', True)
                if 'update_fields' in kwargs:
                    if isinstance(kwargs['update_fields'], list):
                        kwargs['update_fields'].append('code')
                else:
                    kwargs.update({'update_fields': ['code']})

                self.auto_create_goods_issue(self)
        # hit DB
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Product Modification'
        verbose_name_plural = 'Product Modification'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class CurrentComponent(SimpleAbstractModel):
    product_modified = models.ForeignKey(
        ProductModification, on_delete=models.CASCADE, related_name='current_components'
    )
    order = models.IntegerField(default=1)
    component_text_data = models.JSONField(default=dict) # {'title': ...; 'description':...}
    component_product = models.ForeignKey('saledata.Product', on_delete=models.CASCADE, null=True)
    component_product_data = models.JSONField(default=dict)
    component_quantity = models.IntegerField()
    is_added_component = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Current Component'
        verbose_name_plural = 'Current Components'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


class CurrentComponentDetail(SimpleAbstractModel):
    current_component = models.ForeignKey(
        CurrentComponent, on_delete=models.CASCADE, related_name='current_components_detail', null=True
    )

    component_prd_wh = models.ForeignKey(
        'saledata.ProductWareHouse', on_delete=models.CASCADE, null=True
    )
    component_prd_wh_quantity = models.FloatField(default=0)

    component_prd_wh_lot = models.ForeignKey(
        'saledata.ProductWareHouseLot', on_delete=models.CASCADE, null=True
    )
    component_prd_wh_lot_data = models.JSONField(default=dict)
    component_prd_wh_lot_quantity = models.FloatField(default=0)

    component_prd_wh_serial = models.ForeignKey(
        'saledata.ProductWareHouseSerial', on_delete=models.CASCADE, null=True
    )
    component_prd_wh_serial_data = models.JSONField(default=dict)

    class Meta:
        verbose_name = 'Current Component Detail'
        verbose_name_plural = 'Current Components Detail'
        default_permissions = ()
        permissions = ()


class RemovedComponent(SimpleAbstractModel):
    product_modified = models.ForeignKey(
        ProductModification, on_delete=models.CASCADE, related_name='removed_components'
    )
    order = models.IntegerField(default=1)
    component_text_data = models.JSONField(default=dict)
    component_product = models.ForeignKey('saledata.Product', on_delete=models.CASCADE, null=True)
    component_product_data = models.JSONField(default=dict)
    component_quantity = models.IntegerField()

    class Meta:
        verbose_name = 'Removed Component'
        verbose_name_plural = 'Removed Components'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


class RemovedComponentDetail(SimpleAbstractModel):
    removed_component = models.ForeignKey(
        RemovedComponent, on_delete=models.CASCADE, related_name='removed_components_detail', null=True
    )

    component_prd_wh = models.ForeignKey(
        'saledata.ProductWareHouse', on_delete=models.CASCADE, null=True
    )
    component_prd_wh_quantity = models.FloatField(default=0)

    component_prd_wh_lot = models.ForeignKey(
        'saledata.ProductWareHouseLot', on_delete=models.CASCADE, null=True
    )
    component_prd_wh_lot_data = models.JSONField(default=dict)
    component_prd_wh_lot_quantity = models.FloatField(default=0)

    component_prd_wh_serial = models.ForeignKey(
        'saledata.ProductWareHouseSerial', on_delete=models.CASCADE, null=True
    )
    component_prd_wh_serial_data = models.JSONField(default=dict)

    class Meta:
        verbose_name = 'Removed Component Detail'
        verbose_name_plural = 'Removed Components Detail'
        default_permissions = ()
        permissions = ()
