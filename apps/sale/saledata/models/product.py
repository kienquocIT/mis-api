from django.db import models
from apps.shared import DataAbstractModel, MasterDataAbstractModel


# Create your models here.
class ProductType(MasterDataAbstractModel):
    description = models.CharField(verbose_name='description', blank=True, max_length=200)
    is_default = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'ProductType'
        verbose_name_plural = 'ProductTypes'
        ordering = ('code',)
        default_permissions = ()
        permissions = ()
