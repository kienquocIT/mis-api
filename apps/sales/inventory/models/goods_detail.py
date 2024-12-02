from django.db import models
from apps.shared import DataAbstractModel


class GoodsDetail(DataAbstractModel):
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        related_name='goods_detail_product',
    )
    product_data = models.JSONField(default=dict)
    warehouse = models.ForeignKey(
        'saledata.WareHouse',
        on_delete=models.CASCADE,
        related_name='goods_detail_warehouse',
    )
    warehouse_data = models.JSONField(default=dict)
    uom = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        related_name='goods_detail_uom',
    )
    uom_data = models.JSONField(default=dict)
    goods_receipt = models.ForeignKey(
        'inventory.GoodsReceipt',
        on_delete=models.CASCADE,
        related_name='goods_detail_goods_receipt',
    )
    goods_receipt_data = models.JSONField(default=dict)
    purchase_request = models.ForeignKey(
        'purchasing.PurchaseRequest',
        on_delete=models.CASCADE,
        related_name='goods_detail_purchase_request',
        null=True
    )
    purchase_request_data = models.JSONField(default=dict)
    lot = models.ForeignKey(
        'saledata.ProductWareHouseLot',
        on_delete=models.CASCADE,
        related_name='goods_detail_lot',
        null=True
    )
    lot_data = models.JSONField(default=dict)
    imported_sn_quantity = models.FloatField(default=0)
    receipt_quantity = models.FloatField(default=0)
    status = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Goods Detail'
        verbose_name_plural = 'Goods Detail'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
