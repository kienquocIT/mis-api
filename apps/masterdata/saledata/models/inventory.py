from django.db import models

from apps.shared import MasterDataAbstractModel, WAREHOUSE_TYPE

__all__ = [
    'WareHouse',
]


class WareHouse(MasterDataAbstractModel):
    remarks = models.TextField(
        blank=True,
        verbose_name='Description of this records',
    )

    city = models.ForeignKey(
        'base.City',
        on_delete=models.CASCADE,
        null=True,
        default=None,
        related_name='warehouse_city'
    )

    district = models.ForeignKey(
        'base.District',
        on_delete=models.CASCADE,
        null=True,
        default=None,
        related_name='warehouse_district'
    )

    ward = models.ForeignKey(
        'base.Ward',
        on_delete=models.CASCADE,
        null=True,
        default=None,
        related_name='warehouse_ward'
    )

    address = models.CharField(
        max_length=500,
        default='',
        blank=True
    )
    full_address = models.CharField(
        max_length=1000,
        default='',
        blank=True
    )

    agency = models.ForeignKey(
        'saledata.Account',
        on_delete=models.CASCADE,
        null=True,
        default=None,
        related_name='warehouse_agency'
    )

    warehouse_type = models.SmallIntegerField(
        choices=WAREHOUSE_TYPE,
        default=0,
    )

    products = models.ManyToManyField(
        'saledata.Product',
        through='saledata.ProductWareHouse',
        symmetrical=False,
        blank=True,
        related_name='products_of_warehouse',
    )
    is_dropship = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'WareHouse storage'
        verbose_name_plural = 'WareHouse storage'
        ordering = ('title',)
        default_permissions = ()
        permissions = ()

    def save(self, *args, **kwargs):
        # auto create code (temporary)
        warehouse = WareHouse.objects.filter_current(
            fill__tenant=True,
            fill__company=True,
        ).count()
        char = "W"
        if not self.code:
            temper = "%04d" % (warehouse + 1)  # pylint: disable=C0209
            code = f"{char}{temper}"
            self.code = code
        super().save(*args, **kwargs)
