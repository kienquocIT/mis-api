from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.shared import DataAbstractModel, SimpleAbstractModel, MasterDataAbstractModel

__all__ = [
    'ProductType', 'ProductCategory', 'UnitOfMeasureGroup', 'UnitOfMeasure', 'Product', 'Expense',
    'ExpensePrice', 'ExpenseRole', 'ProductMeasurements', 'ProductProductType'
]


TRACEABILITY_METHOD_SELECTION = [
    (0, _('None')),
    (1, _('Batch/Lot number')),
    (2, _('Serial number'))
]


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


class UnitOfMeasureGroup(MasterDataAbstractModel):
    is_default = models.BooleanField(default=False)
    uom_reference = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        verbose_name="uom reference",
        help_text="unit of measure in this group which is reference",
        related_name="uom_group_uom_reference",
        null=True
    )

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
    rounding = models.IntegerField(default=4)
    is_referenced_unit = models.BooleanField(default=False, help_text='UoM Group Referenced Unit')

    class Meta:
        verbose_name = 'UnitOfMeasure'
        verbose_name_plural = 'UnitsOfMeasure'
        ordering = ('-group',)
        default_permissions = ()
        permissions = ()


class Product(DataAbstractModel):
    product_choice = models.JSONField(
        default=list,
        help_text='product for sale: 0, inventory: 1, purchase:2'
    )
    avatar = models.TextField(null=True, verbose_name='avatar path')
    description = models.CharField(blank=True, max_length=500)

    warehouses = models.ManyToManyField(
        'saledata.WareHouse',
        through='saledata.ProductWareHouse',
        symmetrical=False,
        blank=True,
        related_name='warehouses_of_product'
    )

    # General
    general_product_types_mapped = models.ManyToManyField(
        ProductType,
        through='ProductProductType',
        symmetrical=False,
        blank=True,
        related_name='product_map_product_types'
    )
    general_product_category = models.ForeignKey(
        ProductCategory,
        null=True,
        on_delete=models.CASCADE,
        related_name='product_category'
    )
    general_uom_group = models.ForeignKey(
        UnitOfMeasureGroup,
        null=True,
        on_delete=models.CASCADE,
        related_name='uom_group'
    )
    general_traceability_method = models.SmallIntegerField(choices=TRACEABILITY_METHOD_SELECTION, default=0)

    width = models.FloatField(null=True)
    height = models.FloatField(null=True)
    length = models.FloatField(null=True)
    volume = models.JSONField(default=dict)
    weight = models.JSONField(default=dict)

    # Sale
    sale_default_uom = models.ForeignKey(
        UnitOfMeasure,
        null=True,
        on_delete=models.CASCADE,
        related_name='sale_default_uom',
        default=None
    )
    sale_tax = models.ForeignKey(
        'saledata.Tax',
        null=True,
        on_delete=models.CASCADE,
        related_name='sale_tax',
        default=None
    )
    sale_currency_using = models.ForeignKey(
        'saledata.Currency',
        null=True,
        on_delete=models.CASCADE,
        related_name='sale_currency_using_for_cost',
        default=None
    )
    sale_cost = models.FloatField(null=True)
    sale_product_price_list = models.JSONField(default=list)

    # Inventory
    inventory_uom = models.ForeignKey(
        UnitOfMeasure,
        null=True,
        on_delete=models.CASCADE,
        related_name='inventory_uom',
        default=None
    )
    inventory_level_min = models.IntegerField(null=True, default=None)
    inventory_level_max = models.IntegerField(null=True, default=None)

    # Purchase
    purchase_default_uom = models.ForeignKey(
        UnitOfMeasure,
        null=True,
        on_delete=models.CASCADE,
        related_name='purchase_default_uom',
        default=None
    )
    purchase_tax = models.ForeignKey(
        'saledata.Tax',
        null=True,
        on_delete=models.CASCADE,
        related_name='purchase_tax',
        default=None
    )
    # Transaction information
    stock_amount = models.FloatField(
        default=0,
        verbose_name="Stock Amount",
        help_text="Total physical amount product in all warehouse",
    )
    wait_delivery_amount = models.FloatField(
        default=0,
        verbose_name='Wait Delivery Amount',
        help_text='Amount product that ordered but not delivered, update when delivery for sale order'
    )
    wait_receipt_amount = models.FloatField(
        default=0,
        verbose_name='Wait Receipt Amount',
        help_text='Amount product that purchased but not receipted, update when goods receipt for purchase order'
    )
    available_amount = models.FloatField(
        default=0,
        verbose_name='Available Stock',
        help_text='Theoretical amount product in warehouse, =(stock_amount - wait_delivery + wait_receipt)'
    )

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    @classmethod
    def update_transaction_information(cls, instance, **kwargs):
        del kwargs['update_transaction_info']
        if 'quantity_purchase' in kwargs:
            instance.wait_receipt_amount += kwargs['quantity_purchase']
            del kwargs['quantity_purchase']
        if 'quantity_receipt' in kwargs:
            instance.wait_receipt_amount -= kwargs['quantity_receipt']
            instance.stock_amount += kwargs['quantity_receipt']
            del kwargs['quantity_receipt']
        if 'quantity_order' in kwargs:
            instance.wait_delivery_amount += kwargs['quantity_order']
            del kwargs['quantity_order']
        if 'quantity_delivery' in kwargs:
            instance.wait_delivery_amount -= kwargs['quantity_delivery']
            instance.stock_amount -= kwargs['quantity_delivery']
            del kwargs['quantity_delivery']
        instance.available_amount = (
                instance.stock_amount - instance.wait_delivery_amount + instance.wait_receipt_amount
        )
        return kwargs

    def save(self, *args, **kwargs):
        if 'update_transaction_info' in kwargs:
            result = self.update_transaction_information(self, **kwargs)
            kwargs = result
        # hit DB
        super().save(*args, **kwargs)


class Expense(MasterDataAbstractModel):
    uom_group = models.ForeignKey(
        UnitOfMeasureGroup,
        verbose_name='Unit of Measure Group apply for expense',
        on_delete=models.CASCADE,
        null=True,
        related_name='expense_uom_group',
        default=None,
    )
    uom = models.ForeignKey(
        UnitOfMeasure,
        verbose_name='Unit of Measure apply for expense',
        on_delete=models.CASCADE,
        null=True,
        related_name='expense_uom',
        default=None,
    )
    price_list = models.ManyToManyField(
        'saledata.Price',
        through="ExpensePrice",
        symmetrical=False,
        blank=True,
        related_name='expenses_map_prices',
        default=None,
    )
    role = models.ManyToManyField(
        'hr.Role',
        through="ExpenseRole",
        symmetrical=False,
        blank=True,
        related_name='expenses_map_roles',
        default=None,
    )

    class Meta:
        verbose_name = 'Expense'
        verbose_name_plural = 'Expenses'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class ExpensePrice(SimpleAbstractModel):
    expense = models.ForeignKey(
        Expense,
        on_delete=models.CASCADE,
        related_name='expense',
        null=True,
    )

    price = models.ForeignKey(
        'saledata.Price',
        on_delete=models.CASCADE,
    )
    currency = models.ForeignKey(
        'saledata.Currency',
        verbose_name='Currency using for expense in price list',
        on_delete=models.CASCADE,
        null=True,
        related_name='expense_price_currency',
    )
    uom = models.ForeignKey(
        UnitOfMeasure,
        on_delete=models.CASCADE,
        null=True,
        related_name='expense_price_uom'
    )
    is_auto_update = models.BooleanField(default=False)
    price_value = models.FloatField()

    class Meta:
        verbose_name = 'Expense Price'
        verbose_name_plural = 'Expense Prices'
        default_permissions = ()
        permissions = ()


class ExpenseRole(SimpleAbstractModel):
    expense = models.ForeignKey(
        Expense,
        on_delete=models.CASCADE,
        null=True,
        related_name='expense_role_expense',
        default=None,
    )
    role = models.ForeignKey(
        'hr.Role',
        on_delete=models.CASCADE,
        null=True,
        related_name='expense_role_role',
        default=None,
    )

    class Meta:
        verbose_name = 'Expense Role'
        verbose_name_plural = 'Expense Roles'
        default_permissions = ()
        permissions = ()


class ProductMeasurements(SimpleAbstractModel):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='product_measure'
    )
    measure = models.ForeignKey(
        'base.BaseItemUnit',
        on_delete=models.CASCADE,
        related_name="product_volume",
        limit_choices_to={'title__in': ['volume', 'weight']}
    )
    value = models.FloatField()


class ProductProductType(SimpleAbstractModel):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='product_product_types'
    )
    product_type = models.ForeignKey(ProductType, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Product ProductTypes'
        verbose_name_plural = 'Products ProductTypes'
        default_permissions = ()
        permissions = ()
