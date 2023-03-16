from django.db import models
from apps.shared import DataAbstractModel, MasterDataAbstractModel


# Create your models here.
class ProductType(MasterDataAbstractModel):
    description = models.CharField(blank=True, max_length=200)
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'ProductType'
        verbose_name_plural = 'ProductTypes'
        ordering = ('date_created',)
        default_permissions = ()
        permissions = ()


class ProductCategory(MasterDataAbstractModel):
    description = models.CharField(blank=True, max_length=200)

    class Meta:
        verbose_name = 'ProductCategory'
        verbose_name_plural = 'ProductCategories'
        ordering = ('date_created',)
        default_permissions = ()
        permissions = ()


class ExpenseType(MasterDataAbstractModel):
    description = models.CharField(blank=True, max_length=200)
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'ExpenseType'
        verbose_name_plural = 'ExpenseTypes'
        ordering = ('date_created',)
        default_permissions = ()
        permissions = ()


class UnitOfMeasure(MasterDataAbstractModel):
    group = models.ForeignKey(
        'saledata.UnitOfMeasureGroup',
        verbose_name='unit of measure group',
        on_delete=models.CASCADE,
        null=False,
        related_name='unitofmeasure_group'
    )
    ratio = models.FloatField(default=1.0)
    rounding = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'UnitOfMeasure'
        verbose_name_plural = 'UnitsOfMeasure'
        ordering = ('-group', '-date_created')
        default_permissions = ()
        permissions = ()


class UnitOfMeasureGroup(MasterDataAbstractModel):
    referenced_unit = models.ForeignKey(
        UnitOfMeasure,
        null=True,
        on_delete=models.CASCADE,
        related_name='unitofmeasuregroup_referenced_unit'
    )

    class Meta:
        verbose_name = 'UnitOfMeasureGroup'
        verbose_name_plural = 'UnitsOfMeasureGroup'
        ordering = ('date_created',)
        default_permissions = ()
        permissions = ()


class Product(DataAbstractModel):
    avatar = models.TextField(
        null=True,
        verbose_name='avatar path'
    )
    general_information = models.JSONField(
        default=dict,
    )
    inventory_information = models.JSONField(
        default=dict,
    )
    sale_infor = models.JSONField(
        default=dict,
    )
    purchase_infor = models.JSONField(
        default=dict,
    )

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ('code',)
        default_permissions = ()
        permissions = ()
