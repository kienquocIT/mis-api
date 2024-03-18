from django.db import models

from apps.core.attachments.models import M2MFilesAbstractModel
from apps.masterdata.saledata.models import SubPeriods
from apps.shared import DataAbstractModel


class GoodsReturn(DataAbstractModel):
    sale_order = models.ForeignKey('saleorder.SaleOrder', on_delete=models.CASCADE)
    note = models.TextField(blank=True)
    delivery = models.ForeignKey('delivery.OrderDeliverySub', on_delete=models.CASCADE, null=True)
    product = models.ForeignKey('saledata.Product', on_delete=models.CASCADE, null=True)
    uom = models.ForeignKey('saledata.UnitOfMeasure', on_delete=models.CASCADE, null=True)
    return_to_warehouse = models.ForeignKey('saledata.WareHouse', on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = 'Goods Return'
        verbose_name_plural = 'Goods Returns'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    def save(self, *args, **kwargs):
        SubPeriods.check_open(self.company_id, self.tenant_id, self.date_created)

        super().save(*args, **kwargs)


class GoodsReturnProductDetail(DataAbstractModel):
    goods_return = models.ForeignKey(GoodsReturn, on_delete=models.CASCADE, related_name='goods_return_product_detail')
    type = models.SmallIntegerField(choices=((0, 'Default'), (1, 'LOT'), (2, 'Serial')), default=0)

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
