from django.db import models
from apps.shared import MasterDataAbstractModel, DataAbstractModel

__all__ = ['ProductType', 'ProductCategory', 'ExpenseType', 'UnitOfMeasureGroup', 'UnitOfMeasure', 'Product', ]


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


class UnitOfMeasureGroup(MasterDataAbstractModel):

    class Meta:
        verbose_name = 'UnitOfMeasureGroup'
        verbose_name_plural = 'UnitsOfMeasureGroup'
        ordering = ('date_created',)
        default_permissions = ()
        permissions = ()


class UnitOfMeasure(MasterDataAbstractModel):
    group = models.ForeignKey(
        UnitOfMeasureGroup,
        verbose_name='unit of measure group',
        on_delete=models.CASCADE,
        null=False,
        related_name='unitofmeasure_group'
    )
    ratio = models.FloatField(default=1.0)
    rounding = models.IntegerField(default=0)
    is_referenced_unit = models.BooleanField(default=False, help_text='UoM Group Referenced Unit')

    class Meta:
        verbose_name = 'UnitOfMeasure'
        verbose_name_plural = 'UnitsOfMeasure'
        ordering = ('-group',)
        default_permissions = ()
        permissions = ()


class Product(MasterDataAbstractModel):
    avatar = models.TextField(
        null=True,
        verbose_name='avatar path'
    )

    # {
    #     'product_type': 'f417bdf6f4db41aea4f69fc5da4573b5',
    #     'product_category': '7e31d31e17594a4fb06295a6c17579f3',
    #     'uom_group': '933e642d8c584349b406942d2cc6697c',
    #     ...
    # }
    general_information = models.JSONField(
        default=dict,
    )

    # {
    #     'default_uom': 'ac19200a6ab84a30aef14dd213ee4716',
    #     ...
    # }
    sale_information = models.JSONField(
        default=dict,
    )

    # {
    #     'uom': 'ac19200a6ab84a30aef14dd213ee4446',
    #     'inventory_level_min': 100,
    #     'inventory_level_max': 500,
    #     ...
    # }
    inventory_information = models.JSONField(
        default=dict,
    )

    # have not developed yet
    purchase_information = models.JSONField(
        default=dict,
    )

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ('date_created',)
        default_permissions = ()
        permissions = ()
