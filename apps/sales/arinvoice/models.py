import json
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.core.company.models import CompanyFunctionNumber
from apps.shared import (
    SimpleAbstractModel, DataAbstractModel, MasterDataAbstractModel,
)
# Create your models here.


INVOICE_EXP = (
    (0, '01GTKT0/001'),
    (1, '01GTKT3/001'),
    (2, '02GTTT0/001'),
    (3, '02GTTT3/001'),
    (4, '03XKNB3/001'),
    (5, '04HGDL3/001'),
    (6, '07KPTQ3/001'),
)


class ARInvoice(DataAbstractModel):
    customer_mapped = models.ForeignKey('saledata.Account', on_delete=models.CASCADE, null=True)
    customer_name = models.CharField(max_length=250, null=True, blank=True)
    sale_order_mapped = models.ForeignKey('saleorder.SaleOrder', on_delete=models.CASCADE)
    posting_date = models.DateTimeField()
    document_date = models.DateTimeField()
    invoice_date = models.DateTimeField()
    invoice_sign = models.CharField(max_length=250)
    invoice_number = models.CharField(max_length=250)
    invoice_example = models.SmallIntegerField(choices=INVOICE_EXP)

    class Meta:
        verbose_name = 'AR Invoice'
        verbose_name_plural = 'AR Invoices'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class ARInvoiceItems(SimpleAbstractModel):
    ar_invoice = models.ForeignKey('ARInvoice', on_delete=models.CASCADE, related_name='ar_invoice_items')
    item_index = models.IntegerField(default=0)

    product_mapped = models.ForeignKey('saledata.Product', on_delete=models.CASCADE, null=True)
    product_mapped_uom = models.ForeignKey('saledata.UnitOfMeasure', on_delete=models.CASCADE, null=True)
    product_mapped_quantity = models.FloatField(default=0)
    product_mapped_unit_price = models.FloatField(default=0)
    product_mapped_tax_value = models.FloatField(default=0)
    product_mapped_subtotal = models.FloatField(default=0)

    discount_name = models.CharField(max_length=250, null=True)
    discount_uom = models.CharField(max_length=250, null=True)
    discount_quantity = models.FloatField(default=0)
    discount_unit_price = models.FloatField(default=0)
    discount_subtotal = models.FloatField(default=0)

    class Meta:
        verbose_name = 'AR Invoice Item'
        verbose_name_plural = 'AR Invoice Items'
        ordering = ()
        default_permissions = ()
        permissions = ()


class ARInvoiceDelivery(SimpleAbstractModel):
    ar_invoice = models.ForeignKey('ARInvoice', on_delete=models.CASCADE, related_name='ar_invoice_deliveries')
    delivery_mapped = models.ForeignKey('delivery.OrderDeliverySub', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'AR Invoice Delivery'
        verbose_name_plural = 'AR Invoice Deliveries'
        ordering = ()
        default_permissions = ()
        permissions = ()
