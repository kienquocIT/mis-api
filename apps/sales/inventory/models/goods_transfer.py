import json
from django.db import models
from rest_framework import serializers
from apps.masterdata.saledata.models import ProductWareHouseLot, ProductWareHouse, ProductWareHouseSerial, Product
from apps.sales.report.models import ReportInventorySub
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

    goods_transfer_datas = models.JSONField(
        help_text=json.dumps(
            [
                {
                    'warehouse': {
                        'id': 'warehouse_id',
                        'title': 'warehouse_title',
                    },
                    'warehouse_product': {  # product in warehouse
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
                    'end_warehouse': {
                        'id': 'end_warehouse_id',
                        'title': 'end_warehouse_title'
                    },
                    'unit_cost': 500000,
                    'subtotal_cost': 1000000,
                    'lot_changes': [],
                    'sn_changes': []
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

    @classmethod
    def prepare_data_for_logging(cls, instance):
        activities_data_out = []
        activities_data_in = []
        for item in instance.goods_transfer.all():
            lot_data = []
            for lot_item in item.lot_data:
                prd_wh_lot = ProductWareHouseLot.objects.filter(id=lot_item['lot_id']).first()
                if prd_wh_lot:
                    lot_data.append({
                        'lot_id': str(prd_wh_lot.id),
                        'lot_number': prd_wh_lot.lot_number,
                        'lot_quantity': lot_item['quantity'],
                        'lot_value': item.unit_cost * lot_item['quantity'],
                        'lot_expire_date': str(prd_wh_lot.expire_date)
                    })
            activities_data_out.append({
                'product': item.product,
                'warehouse': item.warehouse,
                'system_date': instance.date_approved,
                'posting_date': instance.date_approved,
                'document_date': instance.date_approved,
                'stock_type': -1,
                'trans_id': str(instance.id),
                'trans_code': instance.code,
                'trans_title': 'Goods transfer (out)',
                'quantity': item.quantity,
                'cost': item.unit_cost,
                'value': item.unit_cost * item.quantity,
                'lot_data': lot_data
            })
            activities_data_in.append({
                'product': item.product,
                'warehouse': item.end_warehouse,
                'system_date': instance.date_approved,
                'posting_date': instance.date_approved,
                'document_date': instance.date_approved,
                'stock_type': 1,
                'trans_id': str(instance.id),
                'trans_code': instance.code,
                'trans_title': 'Goods transfer (in)',
                'quantity': item.quantity,
                'cost': item.unit_cost,
                'value': item.unit_cost * item.quantity,
                'lot_data': lot_data
            })
        ReportInventorySub.logging_when_stock_activities_happened(
            instance,
            instance.date_approved,
            activities_data_out
        )
        ReportInventorySub.logging_when_stock_activities_happened(
            instance,
            instance.date_approved,
            activities_data_in
        )
        return True

    @classmethod
    def update_source_destination_product_warehouse_obj(cls, item, product_obj, instance):
        try:
            source = product_obj.product_warehouse_product.filter(
                tenant_id=instance.tenant_id, company_id=instance.company_id, warehouse_id=item['warehouse']['id']
            ).first()
            destination = product_obj.product_warehouse_product.filter(
                tenant_id=instance.tenant_id, company_id=instance.company_id, warehouse=item['end_warehouse']['id']
            ).first()
            if not destination:
                destination = ProductWareHouse.objects.create(
                    tenant_id=instance.tenant_id,
                    company_id=instance.company_id,
                    product=product_obj,
                    uom_id=item['uom']['id'],
                    warehouse_id=item['end_warehouse']['id'],
                    tax=None,
                    unit_price=item['unit_cost'],
                    stock_amount=item['quantity'],
                    receipt_amount=item['quantity'],
                    sold_amount=0,
                    picked_ready=0,
                    product_data=item['warehouse_product']['product_data'],
                    warehouse_data=item['end_warehouse'],
                    uom_data=item['uom'],
                    tax_data={}
                )
            else:
                destination.receipt_amount += item['quantity']
                destination.stock_amount = destination.receipt_amount - destination.sold_amount
                destination.save(update_fields=['receipt_amount', 'stock_amount'])

            source.receipt_amount -= item['quantity']
            source.stock_amount = source.receipt_amount - source.sold_amount
            source.save(update_fields=['receipt_amount', 'stock_amount'])
            return source, destination
        except cls.DoesNotExist:
            raise ValueError('Error when trying update source and destination product warehouse obj.')

    @classmethod
    def update_for_lot(cls, item, source, destination, instance):
        lot_data = item['lot_changes']
        all_lot_src = source.product_warehouse_lot_product_warehouse.all()
        all_lot_des = destination.product_warehouse_lot_product_warehouse.all()
        for lot_item in lot_data:
            lot_src_obj = all_lot_src.filter(id=lot_item['lot_id']).first()
            if lot_src_obj and lot_src_obj.quantity_import >= lot_item['quantity']:
                lot_src_obj.quantity_import -= lot_item['quantity']
                lot_src_obj.save(update_fields=['quantity_import'])
                lot_des_obj = all_lot_des.filter(id=lot_item['lot_id']).first()
                if lot_des_obj:
                    lot_des_obj.quantity_import += lot_item['quantity']
                    lot_des_obj.save(update_fields=['quantity_import'])
                else:
                    ProductWareHouseLot.objects.create(
                        tenant_id=instance.tenant_id,
                        company_id=instance.company_id,
                        product_warehouse=destination,
                        lot_number=lot_src_obj.lot_number,
                        quantity_import=lot_item['quantity'],
                        raw_quantity_import=lot_item['quantity'],
                        expire_date=lot_src_obj.expire_date,
                        manufacture_date=lot_src_obj.manufacture_date
                    )
            else:
                raise serializers.ValidationError({'Lot': 'Update Lot failed.'})
        return True

    @classmethod
    def update_for_serial(cls, item, source, destination, instance):
        sn_data = item['sn_changes']
        all_sn_src = source.product_warehouse_serial_product_warehouse.all()
        for sn_id in sn_data:
            sn_src_obj = all_sn_src.filter(id=sn_id).first()
            if sn_src_obj and not sn_src_obj.is_delete:
                sn_src_obj.is_delete = True
                sn_src_obj.save(update_fields=['is_delete'])
                ProductWareHouseSerial.objects.create(
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
            else:
                raise serializers.ValidationError({'Serial': 'Update Serial failed.'})
        return True

    @classmethod
    def update_lot_serial_data_warehouse(cls, instance):
        for item in instance.goods_transfer_datas:
            product_obj = Product.objects.get(id=item['warehouse_product']['product_data']['id'])
            source, destination = cls.update_source_destination_product_warehouse_obj(item, product_obj, instance)
            if product_obj.general_traceability_method == 1:  # lot
                cls.update_for_lot(item, source, destination, instance)
            elif product_obj.general_traceability_method == 2:  # sn
                cls.update_for_serial(item, source, destination, instance)
        return True

    def save(self, *args, **kwargs):
        if self.system_status in [2, 3]:
            if not self.code:
                goods_transfer = GoodsTransfer.objects.filter_current(
                    fill__tenant=True, fill__company=True, is_delete=False
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
    warehouse = models.ForeignKey(
        'saledata.WareHouse',
        on_delete=models.CASCADE,
        related_name='warehouse_goods_transfer',
    )
    warehouse_title = models.CharField(
        max_length=500,
    )
    warehouse_product = models.ForeignKey(
        'saledata.ProductWareHouse',
        on_delete=models.CASCADE,
        related_name='product_warehouse_goods_transfer',
    )

    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        related_name="product_goods_transfer",
    )

    product_title = models.CharField(
        max_length=500,
    )
    end_warehouse = models.ForeignKey(
        'saledata.WareHouse',
        on_delete=models.CASCADE,
        related_name='end_warehouse_goods_transfer',
    )
    end_warehouse_title = models.CharField(
        max_length=500,
    )
    uom = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        related_name='uom_goods_transfer',
    )
    uom_title = models.CharField(
        max_length=500,
    )
    lot_data = models.JSONField(default=list)  # [{'lot_id': ..., 'quantity': ...}]
    sn_data = models.JSONField(default=list)  # [..., ..., ...]
    quantity = models.FloatField()
    unit_cost = models.FloatField()
    subtotal = models.FloatField()

    class Meta:
        verbose_name = 'Goods Transfer Product'
        verbose_name_plural = 'Goods Transfer Products'
        ordering = ()
        default_permissions = ()
        permissions = ()
