from django.db import models
from apps.shared import DataAbstractModel, MasterDataAbstractModel, SimpleAbstractModel


# Create your models here.
class ProductType(MasterDataAbstractModel):  # noqa
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


class Product(DataAbstractModel):
    avatar = models.TextField(
        null=True,
        verbose_name='avatar path'
    )

    # {
    #     'product_type': {'id':..., 'title':..., 'code':...},
    #     'product_category': {'id':..., 'title':..., 'code':...},
    #     'uom_group': {'id':..., 'title':..., 'code':...},
    # }
    general_information = models.JSONField(
        default=dict,
    )

    # {
    #     'default_uom': {'id':..., 'title':..., 'code':...},
    #     'tax_code': {'id':..., 'title':..., 'code':...}
    # }
    sale_information = models.JSONField(
        default=dict,
    )

    # {
    #     'uom': {'id':..., 'title':..., 'code':...},
    #     'inventory_level_min': 100,
    #     'inventory_level_max': 500,
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


# SUB-MODEL FOR PRODUCT GENERAL
class ProductGeneral(SimpleAbstractModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_type = models.ForeignKey(ProductType, on_delete=models.CASCADE)
    product_category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    uom_group = models.ForeignKey(UnitOfMeasureGroup, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Product General'
        verbose_name_plural = 'Products General'
        default_permissions = ()
        permissions = ()


# SUB-MODEL FOR PRODUCT SALE
class ProductSale(SimpleAbstractModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    default_uom = models.ForeignKey(UnitOfMeasure, on_delete=models.CASCADE)
    tax_code = models.ForeignKey('saledata.Tax', on_delete=models.CASCADE)
    currency_using = models.ForeignKey('saledata.Currency', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Product Sale'
        verbose_name_plural = 'Products Sale'
        default_permissions = ()
        permissions = ()


# SUB-MODEL FOR PRODUCT INVENTORY
class ProductInventory(SimpleAbstractModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    uom = models.ForeignKey(UnitOfMeasure, on_delete=models.CASCADE)
    inventory_level_min = models.IntegerField(null=True)
    inventory_level_max = models.IntegerField(null=True)

    class Meta:
        verbose_name = 'Product Inventory'
        verbose_name_plural = 'Products Inventory'
        default_permissions = ()
        permissions = ()
