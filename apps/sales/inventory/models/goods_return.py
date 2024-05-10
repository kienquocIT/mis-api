from django.db import models
from rest_framework import serializers
from apps.sales.delivery.models import DeliveryConfig
from apps.core.attachments.models import M2MFilesAbstractModel
from apps.masterdata.saledata.models import SubPeriods
from apps.sales.inventory.models.goods_return_sub import (
    GoodsReturnSubSerializerForPicking, GoodsReturnSubSerializerForNonPicking,
    GReturnProductInformationHandle, GReturnFinalAcceptanceHandle
)
from apps.shared import DataAbstractModel


class GoodsReturn(DataAbstractModel):
    sale_order = models.ForeignKey('saleorder.SaleOrder', on_delete=models.CASCADE)
    note = models.TextField(blank=True)
    delivery = models.ForeignKey('delivery.OrderDeliverySub', on_delete=models.CASCADE, null=True)
    product = models.ForeignKey('saledata.Product', on_delete=models.CASCADE, null=True)
    uom = models.ForeignKey('saledata.UnitOfMeasure', on_delete=models.CASCADE, null=True)
    return_to_warehouse = models.ForeignKey('saledata.WareHouse', on_delete=models.CASCADE, null=True)
    product_detail_list = models.JSONField(default=list)
    data_item = models.JSONField(default=list)

    class Meta:
        verbose_name = 'Goods Return'
        verbose_name_plural = 'Goods Returns'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

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
            GReturnProductInformationHandle.main_handle(instance=self)
            # handle final acceptance
            GReturnFinalAcceptanceHandle.main_handle(instance=self)

        super().save(*args, **kwargs)


class GoodsReturnProductDetail(DataAbstractModel):
    goods_return = models.ForeignKey(GoodsReturn, on_delete=models.CASCADE, related_name='goods_return_product_detail')
    type = models.SmallIntegerField(choices=((0, 'Default'), (1, 'LOT'), (2, 'Serial')), default=0)

    default_item = models.ForeignKey('delivery.OrderDeliveryProduct', on_delete=models.CASCADE, null=True)
    default_return_number = models.FloatField(default=0)
    default_redelivery_number = models.FloatField(default=0)

    lot_no = models.ForeignKey('saledata.ProductWareHouseLot', on_delete=models.CASCADE, null=True)
    lot_return_number = models.FloatField(default=0)
    lot_redelivery_number = models.FloatField(default=0)

    serial_no = models.ForeignKey('saledata.ProductWareHouseSerial', on_delete=models.CASCADE, null=True)
    is_return = models.BooleanField(default=False)
    is_redelivery = models.BooleanField(default=False)

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
