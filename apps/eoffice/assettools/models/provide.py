__all__ = ['AssetToolsProvide', 'AssetToolsProvideProduct', 'AssetToolsProvideAttachmentFile']

import json
from django.db import models

from apps.core.attachments.models import M2MFilesAbstractModel
from apps.shared import DataAbstractModel, SimpleAbstractModel


class AssetToolsProvide(DataAbstractModel):
    remark = models.CharField(
        verbose_name='Descriptions',
        max_length=500,
        null=True,
        blank=True
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
    complete_delivered = models.BooleanField(
        verbose_name='Complete Delivered',
        help_text='request has complete delivered',
        default=False, null=True)

    def code_generator(self):
        ast_p = AssetToolsProvide.objects.filter_current(
            fill__tenant=True,
            fill__company=True,
            is_delete=False,
            system_status__gte=2
        ).count()
        if not self.code:
            char = "ATP"
            num_quotient, num_remainder = divmod(ast_p, 1000)
            code = f"{char}{num_remainder + 1:03d}"
            if num_quotient > 0:
                code += f".{num_quotient}"
            self.code = code

    def before_save(self):
        if not self.code:
            self.code_generator()

    def save(self, *args, **kwargs):
        if self.system_status >= 2:
            self.before_save()
            if 'update_fields' in kwargs:
                if isinstance(kwargs['update_fields'], list):
                    kwargs['update_fields'].append('code')
            else:
                kwargs.update({'update_fields': ['code']})
        super().save(*args, **kwargs)

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
        verbose_name='Product of Asset, Tools provide',
        related_name='asset_provide_map_product',
    )
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        verbose_name='Product need provide',
        related_name='product_map_asset_provide',
    )
    order = models.IntegerField(
        default=1
    )
    product_remark = models.CharField(
        verbose_name='descriptions',
        max_length=500,
        null=True,
        blank=True,
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
        verbose_name='Quantity of user request',
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
    delivered = models.FloatField(default=0, verbose_name='Product is delivered')

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
                "title": str(self.product.title),
                "code": self.product.code,
                "is_inventory": self.product.product_choice == 1,
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


class AssetToolsProvideAttachmentFile(M2MFilesAbstractModel):
    asset_tools_provide = models.ForeignKey(
        'assettools.AssetToolsProvide',
        on_delete=models.CASCADE,
        verbose_name='Attachment file of Asset, Tools provide'
    )

    @classmethod
    def get_doc_field_name(cls):
        # field name là foreignkey của request trên bảng này
        return 'asset_tools_provide'

    class Meta:
        verbose_name = 'Asset, Tools provide attachments'
        verbose_name_plural = 'Asset, Tools provide attachments'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
