from django.db import models

from apps.shared import MasterDataAbstractModel
__all__ = [
    'WareHouse',
]


class WareHouse(MasterDataAbstractModel):
    remarks = models.TextField(
        blank=True,
        verbose_name='Description of this records',
    )

    products = models.ManyToManyField(
        'saledata.Product',
        through='saledata.ProductWareHouse',
        symmetrical=False,
        blank=True,
        related_name='products_of_warehouse',
    )

    class Meta:
        verbose_name = 'WareHouse storage'
        verbose_name_plural = 'WareHouse storage'
        ordering = ('title',)
        default_permissions = ()
        permissions = ()
