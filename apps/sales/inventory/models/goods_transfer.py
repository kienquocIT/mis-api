import json
from django.db import models
from rest_framework import serializers
from apps.masterdata.saledata.models import ProductWareHouseLot, ProductWareHouse, ProductWareHouseSerial, Product, \
    SubPeriods
from apps.sales.report.models import ReportStockLog
from apps.shared import DataAbstractModel, GOODS_TRANSFER_TYPE, MasterDataAbstractModel

__all__ = ['GoodsTransfer', 'GoodsTransferProduct']


class GoodsTransfer(DataAbstractModel):
    goods_transfer_type = models.SmallIntegerField(
        default=0,
        choices=GOODS_TRANSFER_TYPE,
        help_text='choices= ' + str(GOODS_TRANSFER_TYPE),
    )
    note = models.CharField(
        max_length=500,
        null=True,
        blank=True
    )
    agency = models.ForeignKey(
        'saledata.Account',
        on_delete=models.CASCADE,
        related_name='goods_transfer_agency',
        null=True,
    )
    date_transfer = models.DateTimeField(null=True)

    class Meta:
        verbose_name = 'Goods Transfer'
        verbose_name_plural = 'Goods Transfer'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    @classmethod
    def prepare_data_for_logging(cls, instance):
        activities_data_out = []
        activities_data_in = []
        for item in instance.goods_transfer.all():
            if item.product.general_traceability_method == 0:
                casted_quantity = ReportStockLog.cast_quantity_to_unit(item.uom, item.quantity)
                casted_cost = (item.unit_cost * item.quantity / casted_quantity) if casted_quantity > 0 else 0
                activities_data_out.append({
                    'sale_order': item.sale_order,
                    'product': item.product,
                    'warehouse': item.warehouse,
                    'system_date': instance.date_approved,
                    'posting_date': instance.date_approved,
                    'document_date': instance.date_approved,
                    'stock_type': -1,
                    'trans_id': str(instance.id),
                    'trans_code': instance.code,
                    'trans_title': 'Goods transfer (out)',
                    'quantity': casted_quantity,
                    'cost': 0,  # theo gia cost
                    'value': 0,  # theo gia cost
                    'lot_data': {}
                })
                activities_data_in.append({
                    'sale_order': item.sale_order,
                    'product': item.product,
                    'warehouse': item.end_warehouse,
                    'system_date': instance.date_approved,
                    'posting_date': instance.date_approved,
                    'document_date': instance.date_approved,
                    'stock_type': 1,
                    'trans_id': str(instance.id),
                    'trans_code': instance.code,
                    'trans_title': 'Goods transfer (in)',
                    'quantity': casted_quantity,
                    'cost': casted_cost,
                    'value': casted_cost * casted_quantity,
                    'lot_data': {}
                })
            if item.product.general_traceability_method == 1:
                for lot_item in item.lot_data:
                    prd_wh_lot = ProductWareHouseLot.objects.filter(id=lot_item['lot_id']).first()
                    if prd_wh_lot:
                        lot_data = {
                            'lot_id': str(prd_wh_lot.id),
                            'lot_number': prd_wh_lot.lot_number,
                            'lot_quantity': lot_item['quantity'],
                            'lot_value': item.unit_cost * lot_item['quantity'],
                            'lot_expire_date': str(prd_wh_lot.expire_date) if prd_wh_lot.expire_date else None
                        }
                        casted_quantity = ReportStockLog.cast_quantity_to_unit(item.uom, lot_item['quantity'])
                        casted_cost = (
                                item.unit_cost * lot_item['quantity'] / casted_quantity
                        ) if lot_item['quantity'] > 0 else 0
                        activities_data_out.append({
                            'sale_order': item.sale_order,
                            'product': item.product,
                            'warehouse': item.warehouse,
                            'system_date': instance.date_approved,
                            'posting_date': instance.date_approved,
                            'document_date': instance.date_approved,
                            'stock_type': -1,
                            'trans_id': str(instance.id),
                            'trans_code': instance.code,
                            'trans_title': 'Goods transfer (out)',
                            'quantity': casted_quantity,
                            'cost': 0,  # theo gia cost
                            'value': 0,  # theo gia cost
                            'lot_data': lot_data
                        })
                        activities_data_in.append({
                            'sale_order': item.sale_order,
                            'product': item.product,
                            'warehouse': item.end_warehouse,
                            'system_date': instance.date_approved,
                            'posting_date': instance.date_approved,
                            'document_date': instance.date_approved,
                            'stock_type': 1,
                            'trans_id': str(instance.id),
                            'trans_code': instance.code,
                            'trans_title': 'Goods transfer (in)',
                            'quantity': casted_quantity,
                            'cost': casted_cost,
                            'value': casted_cost * casted_quantity,
                            'lot_data': lot_data
                        })
            if item.product.general_traceability_method == 2:
                casted_quantity = ReportStockLog.cast_quantity_to_unit(item.uom, item.quantity)
                casted_cost = (item.unit_cost * item.quantity / casted_quantity) if casted_quantity > 0 else 0
                activities_data_out.append({
                    'sale_order': item.sale_order,
                    'product': item.product,
                    'warehouse': item.warehouse,
                    'system_date': instance.date_approved,
                    'posting_date': instance.date_approved,
                    'document_date': instance.date_approved,
                    'stock_type': -1,
                    'trans_id': str(instance.id),
                    'trans_code': instance.code,
                    'trans_title': 'Goods transfer (out)',
                    'quantity': casted_quantity,
                    'cost': 0,  # theo gia cost
                    'value': 0,  # theo gia cost
                    'lot_data': {}
                })
                activities_data_in.append({
                    'sale_order': item.sale_order,
                    'product': item.product,
                    'warehouse': item.end_warehouse,
                    'system_date': instance.date_approved,
                    'posting_date': instance.date_approved,
                    'document_date': instance.date_approved,
                    'stock_type': 1,
                    'trans_id': str(instance.id),
                    'trans_code': instance.code,
                    'trans_title': 'Goods transfer (in)',
                    'quantity': casted_quantity,
                    'cost': casted_cost,
                    'value': casted_cost * casted_quantity,
                    'lot_data': {}
                })
        ReportStockLog.logging_inventory_activities(
            instance,
            instance.date_approved,
            activities_data_out
        )
        ReportStockLog.logging_inventory_activities(
            instance,
            instance.date_approved,
            activities_data_in
        )
        return True

    @classmethod
    def update_source_destination_product_warehouse_obj(cls, item, instance):
        try:
            source = item.product.product_warehouse_product.filter(
                tenant_id=instance.tenant_id, company_id=instance.company_id, warehouse=item.warehouse
            ).first()
            destination = item.product.product_warehouse_product.filter(
                tenant_id=instance.tenant_id, company_id=instance.company_id, warehouse=item.end_warehouse
            ).first()
            if not destination:
                destination = ProductWareHouse.objects.create(
                    tenant_id=instance.tenant_id,
                    company_id=instance.company_id,
                    product=item.product,
                    uom=item.uom,
                    warehouse=item.end_warehouse,
                    tax=None,
                    unit_price=item.unit_cost,
                    stock_amount=item.quantity,
                    receipt_amount=item.quantity,
                    sold_amount=0,
                    picked_ready=0,
                    product_data={
                        'id': item.product_id, 'code': item.product.code, 'title': item.product.title
                    },
                    warehouse_data={
                        'id': item.end_warehouse_id, 'code': item.end_warehouse.code, 'title': item.end_warehouse.title
                    },
                    uom_data={
                        'id': item.uom_id, 'code': item.uom.code, 'title': item.uom.title
                    },
                    tax_data={}
                )
            else:
                destination.receipt_amount += item.quantity
                destination.stock_amount = destination.receipt_amount - destination.sold_amount
                destination.save(update_fields=['receipt_amount', 'stock_amount'])

            source.receipt_amount -= item.quantity
            source.stock_amount = source.receipt_amount - source.sold_amount
            source.save(update_fields=['receipt_amount', 'stock_amount'])
            return source, destination
        except cls.DoesNotExist:
            raise ValueError('Error when trying update source and destination product warehouse obj.')

    @classmethod
    def update_for_lot(cls, item, source, destination, instance):
        all_lot_src = source.product_warehouse_lot_product_warehouse.all()
        all_lot_des = destination.product_warehouse_lot_product_warehouse.all()
        bulk_info = []
        for lot_item in item.lot_data:
            lot_src_obj = all_lot_src.filter(id=lot_item['lot_id']).first()
            if lot_src_obj and lot_src_obj.quantity_import >= lot_item['quantity']:
                lot_src_obj.quantity_import -= lot_item['quantity']
                lot_src_obj.save(update_fields=['quantity_import'])
                lot_des_obj = all_lot_des.filter(id=lot_item['lot_id']).first()
                if lot_des_obj:
                    lot_des_obj.quantity_import += lot_item['quantity']
                    lot_des_obj.save(update_fields=['quantity_import'])
                else:
                    bulk_info.append(
                        ProductWareHouseLot(
                            tenant_id=instance.tenant_id,
                            company_id=instance.company_id,
                            product_warehouse=destination,
                            lot_number=lot_src_obj.lot_number,
                            quantity_import=lot_item['quantity'],
                            expire_date=lot_src_obj.expire_date,
                            manufacture_date=lot_src_obj.manufacture_date
                        )
                    )
            else:
                raise serializers.ValidationError({'Lot': 'Update Lot failed.'})
        ProductWareHouseLot.objects.bulk_create(bulk_info)
        return True

    @classmethod
    def update_for_serial(cls, item, source, destination, instance):
        all_sn_src = source.product_warehouse_serial_product_warehouse.all()
        bulk_info = []
        for sn_id in item.sn_data:
            sn_src_obj = all_sn_src.filter(id=sn_id).first()
            if sn_src_obj and not sn_src_obj.is_delete:
                sn_src_obj.is_delete = True
                sn_src_obj.save(update_fields=['is_delete'])
                bulk_info.append(
                    ProductWareHouseSerial(
                        tenant_id=instance.tenant_id,
                        company_id=instance.company_id,
                        product_warehouse=destination,
                        vendor_serial_number=sn_src_obj.vendor_serial_number,
                        serial_number=sn_src_obj.serial_number,
                        expire_date=sn_src_obj.expire_date,
                        manufacture_date=sn_src_obj.manufacture_date,
                        warranty_start=sn_src_obj.warranty_start,
                        warranty_end=sn_src_obj.warranty_end
                    )
                )
            else:
                raise serializers.ValidationError({'Serial': 'Update Serial failed.'})
        ProductWareHouseSerial.objects.bulk_create(bulk_info)
        return True

    @classmethod
    def update_lot_serial_data_warehouse(cls, instance):
        for item in instance.goods_transfer.all():
            source, destination = cls.update_source_destination_product_warehouse_obj(item, instance)
            if item.product.general_traceability_method == 1:  # lot
                cls.update_for_lot(item, source, destination, instance)
            elif item.product.general_traceability_method == 2:  # sn
                cls.update_for_serial(item, source, destination, instance)
        return True

    def save(self, *args, **kwargs):
        SubPeriods.check_open(
            self.company_id,
            self.tenant_id,
            self.date_approved if self.date_approved else self.date_created
        )

        if self.system_status in [2, 3]:
            if not self.code:
                goods_transfer = GoodsTransfer.objects.filter_current(
                    fill__tenant=True, fill__company=True, is_delete=False, system_status=3
                ).count()
                code = f"GT000{goods_transfer + 1}"
                self.code = code

                if 'update_fields' in kwargs:
                    if isinstance(kwargs['update_fields'], list):
                        kwargs['update_fields'].append('code')
                else:
                    kwargs.update({'update_fields': ['code']})

                self.prepare_data_for_logging(self)
                self.update_lot_serial_data_warehouse(self)
        # hit DB
        super().save(*args, **kwargs)


class GoodsTransferProduct(MasterDataAbstractModel):
    goods_transfer = models.ForeignKey(
        GoodsTransfer,
        on_delete=models.CASCADE,
        related_name='goods_transfer',
    )
    product_warehouse = models.ForeignKey(
        'saledata.ProductWareHouse',
        on_delete=models.CASCADE,
        related_name='product_warehouse_goods_transfer',
    )

    warehouse = models.ForeignKey(
        'saledata.WareHouse',
        on_delete=models.CASCADE,
        related_name='warehouse_goods_transfer',
    )

    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        related_name="product_goods_transfer",
    )

    sale_order = models.ForeignKey(
        'saleorder.SaleOrder',
        on_delete=models.CASCADE,
        related_name="sale_order_goods_transfer",
        null=True
    )

    end_warehouse = models.ForeignKey(
        'saledata.WareHouse',
        on_delete=models.CASCADE,
        related_name='end_warehouse_goods_transfer',
    )

    uom = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        related_name='uom_goods_transfer',
    )

    lot_data = models.JSONField(default=list)  # [{'lot_id': ..., 'quantity': ...}]
    sn_data = models.JSONField(default=list)  # [..., ..., ...]
    quantity = models.FloatField(default=0)
    unit_cost = models.FloatField(default=0)
    subtotal = models.FloatField(default=0)

    class Meta:
        verbose_name = 'Goods Transfer Product'
        verbose_name_plural = 'Goods Transfer Products'
        ordering = ()
        default_permissions = ()
        permissions = ()
