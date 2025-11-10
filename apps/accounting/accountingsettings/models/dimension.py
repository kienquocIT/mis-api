from django.db import models
from apps.shared import MasterDataAbstractModel

__all__ = [
    'DimensionDefinition',
    'DimensionValue',
]

class DimensionDefinition(MasterDataAbstractModel):

    class Meta:
        verbose_name = 'Dimension Definition'
        verbose_name_plural = 'Dimension Definitions'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class DimensionValue(MasterDataAbstractModel):
    dimension = models.ForeignKey(
        'DimensionDefinition',
        on_delete=models.CASCADE,
        related_name='dimension_values',
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="child_values",
        verbose_name="",
        null=True,
    )
    allow_posting = models.BooleanField()
    related_app_id = models.UUIDField(null=True, help_text='uuid of the related model record')
    related_app_code = models.TextField(null=True, help_text='Code of the related model, example: producttype, ....')

    class Meta:
        verbose_name = 'Dimension Value'
        verbose_name_plural = 'Dimension Value'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
