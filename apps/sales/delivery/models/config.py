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
    lead_picking = models.ForeignKey(
        'hr.Employee',
        on_delete=models.CASCADE,
        verbose_name="leader_picking",
        related_name="delivery_config_lead_picking",
        default=None,
        null=True,
        help_text="Picking leadership"
    )
    lead_delivery = models.ForeignKey(
        'hr.Employee',
        on_delete=models.CASCADE,
        verbose_name="lead_delivery",
        related_name="delivery_config_lead_delivery",
        default=None,
        null=True,
        help_text="Picking leadership"
    )
    person_picking = models.JSONField(
        default=dict, verbose_name='list of employee can pick package',
        null=True
    )
    person_delivery = models.JSONField(
        default=dict, verbose_name='list of employee can pick package',
        null=True
    )

    class Meta:
        verbose_name = 'Delivery Config of Company'
        verbose_name_plural = 'Delivery Config of Company'
        default_permissions = ()
        permissions = ()
