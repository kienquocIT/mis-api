from django.db import models

from apps.shared import MasterDataAbstractModel
from .product import Product

__all__ = [
    'WareHouse',
    'WareHouseStock'
]


class WareHouse(MasterDataAbstractModel):
    remarks = models.TextField(
        blank=True,
        verbose_name='Description of this records',
    )

    class Meta:
        verbose_name = 'WareHouse storage'
        verbose_name_plural = 'WareHouse storage'
        ordering = ('title',)
        default_permissions = ()
        permissions = ()


class WareHouseStock(MasterDataAbstractModel):
    warehouse = models.ForeignKey(
        WareHouse,
        on_delete=models.CASCADE,
        verbose_name="Warehouse",
        related_name="warehouse_stock_warehouse",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name="Product",
        related_name="warehouse_stock_product",
    )
    stock = models.FloatField(
        verbose_name="Stock",
        help_text="Stock of product",
    )

    class Meta:
        verbose_name = 'WareHouse stock'
        verbose_name_plural = 'WareHouse stock'
        ordering = ('stock',)
        default_permissions = ()
        permissions = ()
