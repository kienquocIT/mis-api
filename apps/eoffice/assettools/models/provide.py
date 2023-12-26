__all__ = ['AssetToolsProvide', 'AssetToolsProvideProduct', 'AssetToolsProvideAttachmentFile']

import json
from django.utils import timezone
from django.db import models

from apps.shared import DataAbstractModel, SimpleAbstractModel, MasterDataAbstractModel


class AssetToolsProvide(DataAbstractModel):
    remark = models.CharField(
        verbose_name='descriptions',
        max_length=500,
        null=True,
    )
    products = models.ManyToManyField(
        'saledata.Product',
        through='AssetToolsProvideProduct',
        symmetrical=False,
        related_name='products_of_asset_provide',
    )
    attachments = models.ManyToManyField(
        'attachments.Files',
        through='AssetToolsProvideAttachmentFile',
        symmetrical=False,
        blank=True,
        related_name='file_of_asset_provide',
    )
    pretax_amount = models.FloatField(
        verbose_name='Pretax amount',
        help_text='',
        null=True,
    )
    taxes = models.FloatField(
        verbose_name='Taxes',
        help_text='',
        null=True,
    )
    total_amount = models.FloatField(
        verbose_name='Total amount',
        help_text='',
        null=True,
    )

    class Meta:
        verbose_name = 'Asset tools provide'
        verbose_name_plural = 'provide asset, tools of employee'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class AssetToolsProvideProduct(SimpleAbstractModel):
    asset_tools_provide = models.ForeignKey(
        'assettools.AssetToolsProvide',
        on_delete=models.CASCADE,
        verbose_name='Product of Asset, Tools provide'
    )
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        verbose_name='Product need provide',
    )
    order = models.IntegerField(
        default=1
    )
    product_remark = models.CharField(
        verbose_name='descriptions',
        max_length=500,
        null=True,
    )
    product_data = models.JSONField(
        default=dict,
        verbose_name='Product Data backup',
        help_text=json.dumps(
            [
                {'id': '', 'title': '', 'code': '', 'remarks': ''}
            ]
        )
    )
    uom = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        verbose_name='',
    )
    uom_data = models.JSONField(
        default=dict,
        verbose_name='Unit of Measure backup',
        help_text=json.dumps(
            {
                'id': '', 'title': '', 'code': '',
            }
        )
    )
    quantity = models.FloatField(
        verbose_name='Quantity need pickup of SaleOrder',
    )
    price = models.FloatField(default=0, verbose_name='Price')
    tax = models.ForeignKey(
        'saledata.Tax',
        on_delete=models.CASCADE,
        verbose_name='',
        null=True
    )
    tax_data = models.JSONField(
        default=dict,
        verbose_name='Tax backup',
        help_text=json.dumps(
            {
                'id': '', 'title': '', 'code': '', 'rate': '',
            }
        )
    )
    subtotal = models.FloatField(default=0, verbose_name='Subtotal price')

    def create_backup_data(self):
        if self.tax and not self.tax_data:
            self.tax_data = {
                "id": str(self.tax_id),
                "title": str(self.tax.title),
                "code": str(self.tax.code),
                "rate": str(self.tax.rate),
            }
        if self.uom and not self.uom_data:
            self.uom_data = {
                "id": str(self.uom_id),
                "title": str(self.uom.title)
            }
        if self.product and not self.product_data:
            self.product_data = {
                "id": str(self.product_id),
                "title": str(self.product.title)
            }

    def before_save(self):
        self.create_backup_data()

    def save(self, *args, **kwargs):
        self.before_save()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Asset, Tools Provide Product'
        verbose_name_plural = 'Asset, Tools Provide Product'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


class AssetToolsProvideAttachmentFile(MasterDataAbstractModel):
    attachment = models.OneToOneField(
        'attachments.Files',
        on_delete=models.CASCADE,
        verbose_name='Asset, Tools provide attachment files',
        help_text='Asset, Tools provide had one/many attachment file',
        related_name='asset_tools_provide_attachment_file',
    )
    asset_tools_provide = models.ForeignKey(
        'assettools.AssetToolsProvide',
        on_delete=models.CASCADE,
        verbose_name='Attachment file of Asset, Tools provide'
    )
    order = models.SmallIntegerField(
        default=1
    )
    date_created = models.DateTimeField(
        default=timezone.now, editable=False,
        help_text='The record created at value',
    )

    class Meta:
        verbose_name = 'Asset, Tools provide attachments'
        verbose_name_plural = 'Asset, Tools provide attachments'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
