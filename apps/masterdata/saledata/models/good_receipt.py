import json
import uuid

from django.db import models

from apps.shared import MasterDataAbstractModel, DataAbstractModel, SimpleAbstractModel

from .accounts import Account
from .product import Product, UnitOfMeasure
from .inventory import WareHouse
from .price import Tax

__all__ = ['GoodReceipt', 'GoodReceiptProduct', 'GoodReceiptAttachment']


class GoodReceipt(DataAbstractModel):
    supplier = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        verbose_name="Supplier",
        related_name="good_receipt_supplier",
        null=True
    )
    posting_date = models.DateField(
        verbose_name="Posting date",
        help_text='Posting date of request when user apply',
    )
    product_list = models.JSONField(
        default=list,
        verbose_name="Line detail",
        help_text='Product list detail of Good receipt format json'
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
    attachments = models.JSONField(
        default=list,
        null=True,
        verbose_name='attachment file',
        help_text=json.dumps(
            ["uuid4", "uuid4"]
        )
    )
    po_code = models.CharField(
        max_length=50,
        verbose_name="PO code",
        help_text='relate to PO code',
        null=True
    )
    # copy_form_po = models.ForeignKey( coming soon
    #     '',
    #     on_delete=models.CASCADE,
    #     verbose_name="Supplier",
    #     related_name="good_receipt_supplier",
    #     null=True
    # )
    po_data = models.JSONField(
        default=list,
        null=True,
        verbose_name='product list from PO',
        help_text=json.dumps(
            [
                {
                    "id": "uuid4",
                    "uom": "uuid4",
                    "quantity": 1,
                    "unit_price": 10.000,
                    "tax": 1.2,
                    "sub_total": 10.000
                },
            ]
        )
    )

    class Meta:
        verbose_name = 'Good receipt'
        verbose_name_plural = 'Good receipt'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class GoodReceiptProduct(MasterDataAbstractModel):
    good_receipt = models.ForeignKey(
        GoodReceipt,
        on_delete=models.CASCADE,
        verbose_name="Good receipt",
        related_name="good_receipt_product_good_receipt",
        null=True
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name="Product",
        related_name="good_receipt_product"
    )
    product_data = models.JSONField(
        default=dict,
        verbose_name='',
        help_text=json.dumps(
            {
                'id': '',
                'title': '',
                'code': '',
            }
        ),
    )
    warehouse = models.ForeignKey(
        WareHouse,
        on_delete=models.CASCADE,
        verbose_name="Warehouse",
        related_name="good_receipt_warehouse"
    )
    warehouse_data = models.JSONField(
        default=dict,
        verbose_name='',
        help_text=json.dumps(
            {
                'id': '',
                'title': '',
                'code': '',
            }
        ),
    )
    uom = models.ForeignKey(
        UnitOfMeasure,
        on_delete=models.CASCADE,
        verbose_name="Unit of Measure",
        related_name="good_receipt_uom"
    )
    uom_data = models.JSONField(
        default=dict,
        verbose_name='',
        help_text=json.dumps(
            {
                'id': '',
                'title': '',
                'code': '',
            }
        ),
    )
    quantity = models.FloatField(
        verbose_name="Quantity",
        help_text="quantity of product",
    )
    unit_price = models.FloatField(
        verbose_name="unit price",
        help_text="price per product"
    )
    tax = models.ForeignKey(
        Tax,
        on_delete=models.CASCADE,
        verbose_name="Tax",
        help_text="Tax per product"
    )
    tax_data = models.JSONField(
        default=dict,
        verbose_name='',
        help_text=json.dumps(
            {
                'id': '',
                'title': '',
                'code': '',
            }
        ),
    )
    subtotal_price = models.FloatField(
        verbose_name="Subtotal price",
        help_text="total amount of unit price * quantity"
    )
    order = models.IntegerField(
        verbose_name="order",
        help_text="sort purpose", null=True, blank=True
    )

    def before_save(self):
        if self.product and not self.product_data:
            self.product_data = {
                'id': str(self.product_id),
                'title': str(self.product.title),
                'code': str(self.product.code),
            }
        if self.warehouse and not self.warehouse_data:
            self.warehouse_data = {
                'id': str(self.warehouse_id),
                'title': str(self.warehouse.title),
                'code': str(self.warehouse.code),
            }
        if self.uom and not self.uom_data:
            self.uom_data = {
                'id': str(self.uom_id),
                'title': str(self.uom.title),
                'code': str(self.uom.code),
            }
        if self.tax and not self.tax_data:
            self.tax_data = {
                'id': str(self.tax_id),
                'title': str(self.tax.title),
                'code': str(self.tax.code),
            }

    def save(self, *args, **kwargs):
        self.before_save()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Good receipt'
        verbose_name_plural = 'Good receipt'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class GoodReceiptAttachment(SimpleAbstractModel):
    good_receipt = models.ForeignKey(
        GoodReceipt,
        on_delete=models.CASCADE,
        verbose_name='good receipt'
    )
    attachment = models.OneToOneField(
        'attachments.Files',
        on_delete=models.CASCADE,
        verbose_name='Good receipt attachment files',
        help_text='Good receipt had one/many attachment file',
        related_name='good_receipt_attachment_file',
    )
    media_file = models.UUIDField(unique=True, default=uuid.uuid4)

    class Meta:
        verbose_name = 'Good receipt Attachment'
        verbose_name_plural = 'Good receipt Attachment'
        default_permissions = ()
        permissions = ()
