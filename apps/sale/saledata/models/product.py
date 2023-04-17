from django.db import models
from apps.shared import MasterDataAbstractModel, DataAbstractModel, SimpleAbstractModel

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
    #     'product_type': 'Sản phẩm',
    #     'product_category': 'Phần mềm',
    #     'uom_group': 'Unit',
    # }
    general_information = models.JSONField(
        default=dict,
    )

    # {
    #     'default_uom': 'Cái',
    #     'tax_code': 'VAT-10'
    # }
    sale_information = models.JSONField(
        default=dict,
    )

    # {
    #     'uom': 'Chục',
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
    product_type = models.ForeignKey(ProductType, null=True, on_delete=models.CASCADE)
    product_category = models.ForeignKey(ProductCategory, null=True, on_delete=models.CASCADE)
    uom_group = models.ForeignKey(UnitOfMeasureGroup, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'ProductGeneral'
        verbose_name_plural = 'ProductsGeneral'
        default_permissions = ()
        permissions = ()


# SUB-MODEL FOR PRODUCT SALE
class ProductSale(SimpleAbstractModel):
    from apps.sale.saledata.models.price import Tax
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    default_uom = models.ForeignKey(UnitOfMeasure, on_delete=models.CASCADE)
    tax_code = models.ForeignKey(Tax, null=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'ProductSale'
        verbose_name_plural = 'ProductsSale'
        default_permissions = ()
        permissions = ()


# SUB-MODEL FOR PRODUCT INVENTORY
class ProductInventory(SimpleAbstractModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    uom = models.ForeignKey(UnitOfMeasure, on_delete=models.CASCADE)
    inventory_min = models.IntegerField(null=True)
    inventory_max = models.IntegerField(null=True)

    class Meta:
        verbose_name = 'ProductInventory'
        verbose_name_plural = 'ProductsInventory'
        default_permissions = ()
        permissions = ()
