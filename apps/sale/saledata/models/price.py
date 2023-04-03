from django.db import models
from apps.shared import MasterDataAbstractModel


# Create your models here.
class TaxCategory(MasterDataAbstractModel):
    description = models.CharField(blank=True, max_length=200)
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'TaxCategory'
        verbose_name_plural = 'TaxCategories'
        ordering = ('date_created',)
        default_permissions = ()
        permissions = ()


class Tax(MasterDataAbstractModel):
    rate = models.FloatField()
    category = models.ForeignKey(
        TaxCategory,
        verbose_name='category of tax',
        on_delete=models.CASCADE,
        null=False,
        related_name='tax_category'
    )
    # type = 0 is Sale
    # type = 1 is Purchase
    # type = 2 is both Sale and Purchase
    type = models.IntegerField()

    class Meta:
        verbose_name = 'Tax'
        verbose_name_plural = 'Taxes'
        ordering = ('date_created',)
        default_permissions = ()
        permissions = ()


class Currency(MasterDataAbstractModel):
    abbreviation = models.CharField(max_length=100)
    rate = models.FloatField(null=True)
    is_default = models.BooleanField(default=False)
    is_primary = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Currency'
        verbose_name_plural = 'Currencies'
        ordering = ('date_created',)
        default_permissions = ()
        permissions = ()
