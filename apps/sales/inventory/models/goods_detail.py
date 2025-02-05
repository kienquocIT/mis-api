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

    @classmethod
    def push_product_info(cls, instance):
        if instance.product:
            instance.product.save(**{
                'update_stock_info': {
                    'quantity_receipt_po': 0,
                    'quantity_receipt_actual': instance.imported_sn_quantity,
                    'system_status': 3,
                },
                'update_fields': ['wait_receipt_amount', 'available_amount', 'stock_amount']
            })
        return True

    def save(self, *args, **kwargs):
        self.push_product_info(instance=self)  # product inventory info
        # hit DB
        super().save(*args, **kwargs)
