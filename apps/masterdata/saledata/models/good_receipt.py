from django.db import models
from django.utils import timezone
from apps.masterdata.saledata.models import Account, Product, WareHouse, UnitOfMeasure
from apps.shared import MasterDataAbstractModel, DataAbstractModel

__all__ = ['GoodReceipt', 'GoodReceiptProduct']


class GoodReceipt(DataAbstractModel):
    supplier = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        verbose_name="Supplier",
        related_name="good_receipt_supplier",
        null=True
    )
    posting_date = models.DateTimeField(
        default=timezone.now,
        help_text='Posting date',
    )
    product_list = models.JSONField(
        default=list,
    )
    pretax_amount = models.FloatField(
        verbose_name="Pretax amount",
        help_text='Amount before tax'
    )
    taxes = models.FloatField(
        verbose_name="Taxes",
        help_text='Tax amount total of all product. formula per product: (price * tax) / 100'
    )
    total_amount = models.FloatField(
        verbose_name="Total amount",
        help_text='pretax amount + taxes'
    )

    class Meta:
        verbose_name = 'Good receipt'
        verbose_name_plural = 'Good receipt'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class GoodReceiptProduct(MasterDataAbstractModel):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name="Product",
        related_name="good_receipt_product"
    )
    warehouse = models.ForeignKey(
        WareHouse,
        on_delete=models.CASCADE,
        verbose_name="Warehouse",
        related_name="good_receipt_warehouse"
    )
    uom = models.ForeignKey(
        UnitOfMeasure,
        on_delete=models.CASCADE,
        verbose_name="Unit of Measure",
        related_name="good_receipt_uom"
    )
    quantity = models.IntegerField(
        verbose_name="Quantity",
        help_text="quantity of product",
    )
    unit_price = models.FloatField(
        verbose_name="unit price",
        help_text="price per product"
    )
    tax = models.FloatField(
        verbose_name="Tax",
        help_text="Tax per product"
    )
    subtotal_price = models.FloatField(
        verbose_name="Subtotal price",
        help_text="total amount of unit price * quantity"
    )
    order = models.IntegerField(
        verbose_name="order",
        help_text="sort purpose", null=True, blank=True
    )

    class Meta:
        verbose_name = 'Good receipt'
        verbose_name_plural = 'Good receipt'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
