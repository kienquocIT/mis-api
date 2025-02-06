from django.db import models
from apps.shared import MasterDataAbstractModel

__all__ = [
    'FixedAssetClassification',
    'FixedAssetClassificationGroup'
]

class FixedAssetClassification(MasterDataAbstractModel):
    group = models.ForeignKey(
        'FixedAssetClassificationGroup',
        verbose_name='Group of Classification',
        related_name='asset_classifications',
        on_delete=models.CASCADE,
        null=True
    )
    is_default = models.BooleanField(default=False)
    class Meta:
        verbose_name = 'AssetClassification'
        verbose_name_plural = 'AssetClassifications'
        ordering = ('code',)

class FixedAssetClassificationGroup(MasterDataAbstractModel):
    is_default = models.BooleanField(default=False)
    class Meta:
        verbose_name = 'AssetClassificationGroup'
        verbose_name_plural = 'AssetClassificationGroups'
        ordering = ('code',)
