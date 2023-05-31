from django.db import models

from apps.shared import SimpleAbstractModel

__all__ = ['DeliveryConfig']


class DeliveryConfig(SimpleAbstractModel):
    company = models.OneToOneField(
        'company.Company', on_delete=models.CASCADE,
        related_name='sales_delivery_config_detail',
    )
    is_picking = models.BooleanField(
        default=False,
        verbose_name='setup Picking before delivery',
    )
    is_partial_ship = models.BooleanField(
        default=False,
        verbose_name='Partial delivery',
    )

    class Meta:
        verbose_name = 'Delivery Config of Company'
        verbose_name_plural = 'Delivery Config of Company'
        default_permissions = ()
        permissions = ()
