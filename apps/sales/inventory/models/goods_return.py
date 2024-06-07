from django.db import models
from rest_framework import serializers
from apps.sales.delivery.models import DeliveryConfig, OrderDeliveryProduct
from apps.core.attachments.models import M2MFilesAbstractModel
from apps.masterdata.saledata.models import SubPeriods
from apps.sales.inventory.models.goods_return_sub import (
    GoodsReturnSubSerializerForPicking, GoodsReturnSubSerializerForNonPicking
)
from apps.sales.inventory.utils import ReturnFinishHandler
from apps.sales.report.models import ReportInventorySub
from apps.shared import DataAbstractModel


class GoodsReturn(DataAbstractModel):
    sale_order = models.ForeignKey('saleorder.SaleOrder', on_delete=models.CASCADE)
    note = models.TextField(blank=True)
    delivery = models.ForeignKey('delivery.OrderDeliverySub', on_delete=models.CASCADE, null=True)
    product_detail_list = models.JSONField(default=list, help_text="data to create mapped items")

    data_line_detail_table = models.JSONField(default=list, help_text="to_quick_load_line_detail_table")

    class Meta:
        verbose_name = 'Goods Return'
        verbose_name_plural = 'Goods Returns'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    @classmethod
    def check_exists(cls, activities_data, data):
        for item in activities_data:
            if all([
                data['product'] == item['product'], data['warehouse'] == item['warehouse'],
                data['system_date'] == item['system_date'], data['posting_date'] == item['posting_date'],
                data['document_date'] == item['document_date'], data['stock_type'] == item['stock_type'],
                data['trans_id'] == item['trans_id'], data['trans_code'] == item['trans_code'],
                data['trans_title'] == item['trans_title']
            ]):
                item['quantity'] += data['quantity']
                item['value'] += item['quantity'] * item['cost']
                return activities_data, True
        return activities_data, False

    @classmethod
    def for_perpetual_inventory(cls, instance):
        product_detail_list = instance.goods_return_product_detail.all()
        activities_data = []
        for item in product_detail_list.filter(type=0):
            delivery_item = ReportInventorySub.objects.filter(
                product=item.product, lot_mapped=item.lot_no, trans_id=str(instance.delivery_id)
            ).first()
            if delivery_item:
                casted_quantity = ReportInventorySub.cast_quantity_to_unit(item.uom, item.default_return_number)
                casted_cost = (
                    delivery_item.current_cost * item.default_return_number / casted_quantity
                ) if casted_quantity > 0 else 0
                data = {
                    'product': item.product,
                    'warehouse': item.return_to_warehouse,
                    'system_date': instance.date_approved,
                    'posting_date': instance.date_approved,
                    'document_date': instance.date_approved,
                    'stock_type': 1,
                    'trans_id': str(instance.id),
                    'trans_code': instance.code,
                    'trans_title': 'Goods return',
                    'quantity': casted_quantity,
                    'cost': casted_cost,
                    'value': casted_quantity * casted_cost,
                    'lot_data': {}
                }
                activities_data, is_append = cls.check_exists(activities_data, data)
                if not is_append:
                    activities_data.append(data)
            else:
                raise serializers.ValidationError({'Delivery info': 'Delivery information is not found.'})
        for item in product_detail_list.filter(type=1):
            print(item.product.code, item.lot_no.lot_number, str(item.delivery_item_id))
            delivery_item = ReportInventorySub.objects.filter(
                product=item.product, lot_mapped=item.lot_no, trans_id=str(instance.delivery_id)
            ).first()
            if delivery_item:
                casted_quantity = ReportInventorySub.cast_quantity_to_unit(item.uom, item.lot_return_number)
                casted_cost = (
                    delivery_item.current_cost * item.lot_return_number / casted_quantity
                ) if casted_quantity > 0 else 0
                data = {
                    'product': item.product,
                    'warehouse': item.return_to_warehouse,
                    'system_date': instance.date_approved,
                    'posting_date': instance.date_approved,
                    'document_date': instance.date_approved,
                    'stock_type': 1,
                    'trans_id': str(instance.id),
                    'trans_code': instance.code,
                    'trans_title': 'Goods return',
                    'quantity': casted_quantity,
                    'cost': casted_cost,
                    'value': casted_quantity * casted_cost,
                    'lot_data': {
                        'lot_id': str(item.lot_no_id),
                        'lot_number': item.lot_no.lot_number,
                        'lot_quantity': casted_quantity,
                        'lot_value': casted_quantity * casted_cost,
                        'lot_expire_date': str(item.lot_no.expire_date) if item.lot_no.expire_date else None
                    }
                }
                activities_data, is_append = cls.check_exists(activities_data, data)
                if not is_append:
                    activities_data.append(data)
            else:
                raise serializers.ValidationError({'Delivery info': 'Delivery information is not found.'})
        for item in product_detail_list.filter(type=2):
            delivery_item = ReportInventorySub.objects.filter(
                product=item.product, lot_mapped=item.lot_no, trans_id=str(instance.delivery_id)
            ).first()
            if delivery_item:
                casted_quantity = ReportInventorySub.cast_quantity_to_unit(item.uom, float(item.is_return))
                casted_cost = (
                    delivery_item.current_cost * float(item.is_return) / casted_quantity
                ) if casted_quantity > 0 else 0
                data = {
                    'product': item.product,
                    'warehouse': item.return_to_warehouse,
                    'system_date': instance.date_approved,
                    'posting_date': instance.date_approved,
                    'document_date': instance.date_approved,
                    'stock_type': 1,
                    'trans_id': str(instance.id),
                    'trans_code': instance.code,
                    'trans_title': 'Goods return',
                    'quantity': casted_quantity,
                    'cost': casted_cost,
                    'value': casted_quantity * casted_cost,
                    'lot_data': {}
                }
                activities_data, is_append = cls.check_exists(activities_data, data)
                if not is_append:
                    activities_data.append(data)
            else:
                raise serializers.ValidationError({'Delivery info': 'Delivery information is not found.'})
        return activities_data

    @classmethod
    def for_periodic_inventory(cls, instance):
        product_detail_list = instance.goods_return_product_detail.all()
        activities_data = []
        for item in product_detail_list.filter(type=0):
            casted_quantity = ReportInventorySub.cast_quantity_to_unit(item.uom, item.default_return_number)
            casted_cost = (
                    item.cost_for_periodic * item.default_return_number / casted_quantity
            ) if casted_quantity > 0 else 0
            activities_data.append({
                'product': item.product,
                'warehouse': item.return_to_warehouse,
                'system_date': instance.date_approved,
                'posting_date': instance.date_approved,
                'document_date': instance.date_approved,
                'stock_type': 1,
                'trans_id': str(instance.id),
                'trans_code': instance.code,
                'trans_title': 'Goods return',
                'quantity': casted_quantity,
                'cost': casted_cost,
                'value': casted_quantity * casted_cost,
                'lot_data': {}
            })
        for item in product_detail_list.filter(type=1):
            casted_quantity = ReportInventorySub.cast_quantity_to_unit(item.uom, item.lot_return_number)
            casted_cost = (
                    item.cost_for_periodic * item.lot_return_number / casted_quantity
            ) if casted_quantity > 0 else 0
            activities_data.append({
                'product': item.product,
                'warehouse': item.return_to_warehouse,
                'system_date': instance.date_approved,
                'posting_date': instance.date_approved,
                'document_date': instance.date_approved,
                'stock_type': 1,
                'trans_id': str(instance.id),
                'trans_code': instance.code,
                'trans_title': 'Goods return',
                'quantity': casted_quantity,
                'cost': casted_cost,
                'value': casted_quantity * casted_cost,
                'lot_data': {
                    'lot_id': str(item.lot_no_id),
                    'lot_number': item.lot_no.lot_number,
                    'lot_quantity': casted_quantity,
                    'lot_value': casted_quantity * casted_cost,
                    'lot_expire_date': str(item.lot_no.expire_date) if item.lot_no.expire_date else None
                }
            })
        for item in product_detail_list.filter(type=2):
            casted_quantity = ReportInventorySub.cast_quantity_to_unit(item.uom, float(item.is_return))
            casted_cost = (
                    item.cost_for_periodic * float(item.is_return) / casted_quantity
            ) if casted_quantity > 0 else 0
            activities_data.append({
                'product': item.product,
                'warehouse': item.return_to_warehouse,
                'system_date': instance.date_approved,
                'posting_date': instance.date_approved,
                'document_date': instance.date_approved,
                'stock_type': 1,
                'trans_id': str(instance.id),
                'trans_code': instance.code,
                'trans_title': 'Goods return',
                'quantity': casted_quantity,
                'cost': casted_cost,
                'value': casted_quantity * casted_cost,
                'lot_data': {}
            })
        return activities_data

    @classmethod
    def prepare_data_for_logging(cls, instance):
        if instance.company.companyconfig.definition_inventory_valuation == 0:
            activities_data = cls.for_perpetual_inventory(instance)
        else:
            activities_data = cls.for_periodic_inventory(instance)

        ReportInventorySub.logging_when_stock_activities_happened(
            instance,
            instance.date_created,
            activities_data
        )
        return True

    def save(self, *args, **kwargs):
        SubPeriods.check_open(
            self.company_id,
            self.tenant_id,
            self.date_approved if self.date_approved else self.date_created
        )
        if self.system_status in [2, 3]:
            if not self.code:
                count = GoodsReturn.objects.filter_current(
                    fill__tenant=True, fill__company=True, is_delete=False, system_status=3
                ).count()
                self.code = f"GRT00{count + 1}"

                if 'update_fields' in kwargs:
                    if isinstance(kwargs['update_fields'], list):
                        kwargs['update_fields'].append('code')
                else:
                    kwargs.update({'update_fields': ['code']})

            config = DeliveryConfig.objects.filter_current(fill__tenant=True, fill__company=True).first()
            if config:
                if config.is_picking is True:
                    GoodsReturnSubSerializerForPicking.update_delivery(self)
                else:
                    GoodsReturnSubSerializerForNonPicking.update_delivery(self)
            else:
                raise serializers.ValidationError({"Config": 'Delivery Config Not Found.'})

            # handle product information
            ReturnFinishHandler.push_product_info(instance=self)
            # handle final acceptance
            ReturnFinishHandler.update_final_acceptance(instance=self)

            self.prepare_data_for_logging(self)

        super().save(*args, **kwargs)


class GoodsReturnProductDetail(DataAbstractModel):
    goods_return = models.ForeignKey(GoodsReturn, on_delete=models.CASCADE, related_name='goods_return_product_detail')
    type = models.SmallIntegerField(choices=((0, 'Default'), (1, 'LOT'), (2, 'Serial')), default=0)

    product = models.ForeignKey('saledata.Product', on_delete=models.CASCADE, null=True)
    uom = models.ForeignKey('saledata.UnitOfMeasure', on_delete=models.CASCADE, null=True)
    return_to_warehouse = models.ForeignKey('saledata.WareHouse', on_delete=models.CASCADE, null=True)

    delivery_item = models.ForeignKey('delivery.OrderDeliveryProduct', on_delete=models.CASCADE, null=True)

    default_return_number = models.FloatField(default=0)
    default_redelivery_number = models.FloatField(default=0)

    lot_no = models.ForeignKey('saledata.ProductWareHouseLot', on_delete=models.CASCADE, null=True)
    lot_return_number = models.FloatField(default=0)
    lot_redelivery_number = models.FloatField(default=0)

    serial_no = models.ForeignKey('saledata.ProductWareHouseSerial', on_delete=models.CASCADE, null=True)
    is_return = models.BooleanField(default=False)
    is_redelivery = models.BooleanField(default=False)

    cost_for_periodic = models.FloatField(default=0)

    class Meta:
        verbose_name = 'Goods Return Product Detail'
        verbose_name_plural = 'Goods Returns Products Detail'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class GoodsReturnAttachmentFile(M2MFilesAbstractModel):
    goods_return = models.ForeignKey(
        GoodsReturn,
        on_delete=models.CASCADE,
        related_name='goods_return_attachments'
    )

    class Meta:
        verbose_name = 'Goods Return attachment'
        verbose_name_plural = 'Goods Return attachments'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
