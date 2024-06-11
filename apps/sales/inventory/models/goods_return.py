from django.db import models
from rest_framework import serializers
from apps.sales.delivery.models import DeliveryConfig
from apps.core.attachments.models import M2MFilesAbstractModel
from apps.masterdata.saledata.models import SubPeriods  # ProductWareHouseLot
from apps.sales.inventory.models.goods_return_sub import (
    GoodsReturnSubSerializerForPicking, GoodsReturnSubSerializerForNonPicking
)
from apps.sales.inventory.utils import ReturnFinishHandler, ReturnHandler
# from apps.sales.report.models import ReportInventorySub
from apps.shared import DataAbstractModel


class GoodsReturn(DataAbstractModel):
    sale_order = models.ForeignKey('saleorder.SaleOrder', on_delete=models.CASCADE)
    note = models.TextField(blank=True)
    delivery = models.ForeignKey('delivery.OrderDeliverySub', on_delete=models.CASCADE, null=True)
    product = models.ForeignKey('saledata.Product', on_delete=models.CASCADE, null=True)
    uom = models.ForeignKey('saledata.UnitOfMeasure', on_delete=models.CASCADE, null=True)
    return_to_warehouse = models.ForeignKey('saledata.WareHouse', on_delete=models.CASCADE, null=True)
    product_detail_list = models.JSONField(default=list)
    data_line_detail = models.JSONField(default=list, help_text="to_quick_load_Line_detail_tab")

    class Meta:
        verbose_name = 'Goods Return'
        verbose_name_plural = 'Goods Returns'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    # @classmethod
    # def prepare_data_for_logging(cls, instance):
    #     product_detail_list = instance.product_detail_list
    #     return_quantity = 0
    #     lot_mapped_id = None
    #     for item in product_detail_list:
    #         if item.get('type') == 0:
    #             return_quantity += item.get('default_return_number', 0)
    #         elif item.get('type') == 1:
    #             return_quantity += item.get('lot_return_number', 0)
    #             lot_mapped_id = item.get('lot_no_id')
    #         elif item.get('type') == 2:
    #             return_quantity += item.get('is_return', 0)
    #
    #     activities_data = []
    #     if instance.company.companyconfig.definition_inventory_valuation == 0:
    #         delivery_product = ReportInventorySub.objects.filter(
    #             lot_mapped_id=lot_mapped_id,
    #             warehouse=instance.return_to_warehouse,
    #             product=instance.product,
    #             trans_id=str(instance.delivery_id)
    #         ).first()
    #         if delivery_product:
    #             delivery_product_cost = delivery_product.cost
    #         else:
    #             delivery_product_cost = 0
    #             # raise serializers.ValidationError({'Delivery info': 'Delivery information is not found.'})
    #     else:
    #         goods_return_cost_input = instance.goods_return_product_detail.first()
    #         if goods_return_cost_input:
    #             delivery_product_cost = goods_return_cost_input.cost_for_periodic
    #         else:
    #             delivery_product_cost = 0
    #             # raise serializers.ValidationError({'Cost': 'Cost is not null.'})
    #
    #     for lot in product_detail_list:
    #         data_type = lot.get('type')
    #         prd_wh_lot = ProductWareHouseLot.objects.filter(id=lot['lot_no_id']).first() if data_type == 1 else None
    #         if prd_wh_lot and data_type == 1:  # is LOT
    #             lot_data = {
    #                 'lot_id': str(prd_wh_lot.id),
    #                 'lot_number': prd_wh_lot.lot_number,
    #                 'lot_quantity': lot['lot_return_number'],
    #                 'lot_value': delivery_product_cost * lot['lot_return_number'],
    #                 'lot_expire_date': str(prd_wh_lot.expire_date) if prd_wh_lot.expire_date else None
    #             }
    #             casted_quantity = ReportInventorySub.cast_quantity_to_unit(
    #                 instance.uom, lot['lot_return_number']
    #             )
    #             casted_cost = (
    #                 delivery_product_cost * lot['lot_return_number'] / casted_quantity
    #             ) if casted_quantity > 0 else 0
    #             activities_data.append({
    #                 'product': instance.product,
    #                 'warehouse': instance.return_to_warehouse,
    #                 'system_date': instance.date_created,
    #                 'posting_date': instance.date_created,
    #                 'document_date': instance.date_created,
    #                 'stock_type': 1,
    #                 'trans_id': str(instance.id),
    #                 'trans_code': instance.code,
    #                 'trans_title': 'Goods return',
    #                 'quantity': casted_quantity,
    #                 'cost': casted_cost,
    #                 'value': casted_quantity * casted_cost,
    #                 'lot_data': lot_data
    #             })
    #
    #     casted_quantity = ReportInventorySub.cast_quantity_to_unit(
    #         instance.uom,
    #         return_quantity
    #     )
    #     casted_cost = (delivery_product_cost * return_quantity / casted_quantity) if casted_quantity > 0 else 0
    #     activities_data.append({
    #         'product': instance.product,
    #         'warehouse': instance.return_to_warehouse,
    #         'system_date': instance.date_created,
    #         'posting_date': instance.date_created,
    #         'document_date': instance.date_created,
    #         'stock_type': 1,
    #         'trans_id': str(instance.id),
    #         'trans_code': instance.code,
    #         'trans_title': 'Goods return',
    #         'quantity': casted_quantity,
    #         'cost': casted_cost,
    #         'value': casted_quantity * casted_cost,
    #         'lot_data': {}
    #     })
    #     ReportInventorySub.logging_when_stock_activities_happened(
    #         instance,
    #         instance.date_created,
    #         activities_data
    #     )
    #     return True

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

            # handle after finish
            # product information
            ReturnFinishHandler.push_product_info(instance=self)
            # final acceptance
            ReturnFinishHandler.update_final_acceptance(instance=self)
            # report
            ReturnFinishHandler.update_report(instance=self)

            # self.prepare_data_for_logging(self)

        # diagram
        ReturnHandler.push_diagram(instance=self)
        # hit DB
        super().save(*args, **kwargs)


class GoodsReturnProductDetail(DataAbstractModel):
    goods_return = models.ForeignKey(GoodsReturn, on_delete=models.CASCADE, related_name='goods_return_product_detail')
    type = models.SmallIntegerField(choices=((0, 'Default'), (1, 'LOT'), (2, 'Serial')), default=0)

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
