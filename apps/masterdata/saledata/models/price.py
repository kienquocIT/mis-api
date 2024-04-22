from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.masterdata.saledata.models.product import Product, UnitOfMeasure, UnitOfMeasureGroup
from apps.shared import DataAbstractModel, MasterDataAbstractModel, SimpleAbstractModel

__all__ = [
    'TaxCategory',
    'Tax',
    'Currency',
    'Price',
    'ProductPriceList',
    'Discount',
    'UnitOfMeasureGroup',
    'PriceListCurrency'
]

PRICE_LIST_TYPE = [
    (0, _('For Sale')),
    (1, _('For Purchase')),
    (2, _('For Expense')),
]


# Create your models here.
class TaxCategory(MasterDataAbstractModel):  # noqa
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
    # type = 0 is 'Sale'
    # type = 1 is 'Purchase'
    # type = 2 is both 'Sale' and 'Purchase'
    tax_type = models.IntegerField()

    class Meta:
        verbose_name = 'Tax'
        verbose_name_plural = 'Taxes'
        ordering = ('date_created',)
        default_permissions = ()
        permissions = ()


class Currency(MasterDataAbstractModel):
    currency = models.ForeignKey('base.Currency', on_delete=models.CASCADE, null=True)
    abbreviation = models.CharField(max_length=100)
    rate = models.FloatField(null=True)
    is_default = models.BooleanField(default=False)
    is_primary = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Currency'
        verbose_name_plural = 'Currencies'
        ordering = ('date_created',)
        unique_together = ('company', 'abbreviation')
        default_permissions = ()
        permissions = ()


class Price(DataAbstractModel):
    auto_update = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    factor = models.FloatField()
    # currency = [
    #     first_id,
    #     second_id,
    #     ...
    # ]
    currency = models.JSONField(default=list)

    currency_current = models.ManyToManyField(
        'saledata.Currency',
        through='PriceListCurrency',
        symmetrical=False,
        blank=True,
        related_name='opportunity_mapped'
    )

    valid_time_start = models.DateTimeField(
        verbose_name='price list will be apply since valid_time_start',
        default=timezone.now,
        null=True
    )
    valid_time_end = models.DateTimeField(
        verbose_name='price list will be end at valid_time_end',
        default='9999-01-01 00:00:00.00',
        null=True
    )
    price_list_type = models.SmallIntegerField(choices=PRICE_LIST_TYPE)
    price_list_mapped = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        default=None,
        related_name='price_parent'
    )
    product = models.ManyToManyField(
        Product,
        through='ProductPriceList',
        symmetrical=False,
        blank=True,
        related_name='price_map_product'
    )
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Price'
        verbose_name_plural = 'Prices'
        ordering = ('date_created',)
        default_permissions = ()
        permissions = ()


class PriceListCurrency(SimpleAbstractModel):
    price = models.ForeignKey(
        Price,
        on_delete=models.CASCADE,
        null=True,
        related_name='price_list'
    )
    currency = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE,
        null=True,
        related_name='price_currency'
    )

    class Meta:
        verbose_name = 'PriceCurrency'
        verbose_name_plural = 'PriceCurrencies'
        ordering = ()
        default_permissions = ()
        permissions = ()


# ProductPriceList
class ProductPriceList(SimpleAbstractModel):
    price_list = models.ForeignKey(
        Price,
        on_delete=models.CASCADE,
        related_name='product_price_price',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='product_price_product',
    )
    price = models.FloatField()
    get_price_from_source = models.BooleanField(default=False)  # True nếu lấy giá từ 1 price_list khác, else False
    currency_using = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE,
        related_name='product_price_currency',
    )
    uom_using = models.ForeignKey(
        UnitOfMeasure,
        on_delete=models.CASCADE,
        related_name='product_price_uom',
    )
    uom_group_using = models.ForeignKey(
        UnitOfMeasureGroup,
        on_delete=models.CASCADE,
        related_name='product_price_uom_group'
    )
    date_created = models.DateTimeField(
        default=timezone.now, editable=False,
        help_text='The record created at value',
    )
    date_modified = models.DateTimeField(
        auto_now_add=True,
        help_text='Date modified this record in last',
    )
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'ProductPriceList'
        verbose_name_plural = 'ProductsPriceList'
        ordering = ('date_created',)
        default_permissions = ()
        permissions = ()


# Discount
class Discount(MasterDataAbstractModel):
    class Meta:
        verbose_name = 'Discount'
        verbose_name_plural = 'Discounts'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
