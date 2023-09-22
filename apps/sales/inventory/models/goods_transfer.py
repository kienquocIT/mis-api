import json

from django.db import models
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
                        'product_data':{
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

    def save(self, *args, **kwargs):
        # auto create code (temporary)
        goods_receipt = GoodsTransfer.objects.filter_current(
            fill__tenant=True,
            fill__company=True,
            is_delete=False
        ).count()
        char = "GT"
        if not self.code:
            temper = "%04d" % (goods_receipt + 1)  # pylint: disable=C0209
            code = f"{char}{temper}"
            self.code = code
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
    quantity = models.FloatField()
    unit_cost = models.FloatField()
    subtotal = models.FloatField()

    class Meta:
        verbose_name = 'Goods Transfer Product'
        verbose_name_plural = 'Goods Transfer Products'
        ordering = ()
        default_permissions = ()
        permissions = ()
