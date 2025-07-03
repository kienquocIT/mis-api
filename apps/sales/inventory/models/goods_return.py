from django.db import models
from rest_framework import serializers
from apps.core.attachments.models import M2MFilesAbstractModel
from apps.masterdata.saledata.models import SubPeriods
from apps.sales.inventory.models.goods_return_sub import (
    GoodsReturnSubSerializerForPicking, GoodsReturnSubSerializerForNonPicking
)
from apps.sales.inventory.utils import ReturnFinishHandler, ReturnHandler
from apps.sales.report.utils.log_for_goods_return import IRForGoodsReturnHandler
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

    def save(self, *args, **kwargs):
        if not kwargs.get('skip_check_period', False):
            SubPeriods.check_period(self.tenant_id, self.company_id)

        if self.system_status in [2, 3]:
            if not self.code:
                self.add_auto_generate_code_to_instance(self, 'GRT[n4]', True)

                if 'update_fields' in kwargs:
                    if isinstance(kwargs['update_fields'], list):
                        kwargs['update_fields'].append('code')
                else:
                    kwargs.update({'update_fields': ['code']})

                if self.system_status == 3:
                    if hasattr(self.company, 'sales_delivery_config_detail'):
                        config = self.company.sales_delivery_config_detail
                        if not config:
                            raise serializers.ValidationError({"Config": 'Delivery Config Not Found.'})
                        if config.is_picking is True:
                            GoodsReturnSubSerializerForPicking.update_delivery(self)
                        else:
                            GoodsReturnSubSerializerForNonPicking.update_delivery(self)

                    # handle after finish
                    # product information
                    ReturnFinishHandler.push_product_info(instance=self)
                    # final acceptance
                    ReturnFinishHandler.update_final_acceptance(instance=self)
                    # report
                    ReturnFinishHandler.update_report(instance=self)

                    IRForGoodsReturnHandler.push_to_inventory_report(self)

        # diagram
        ReturnHandler.push_diagram(instance=self)
        # hit DB
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
