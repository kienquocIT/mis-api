import json

from django.db import models

from apps.shared import DataAbstractModel, SimpleAbstractModel


class AssetToolsDelivery(DataAbstractModel):
    provide = models.ForeignKey(
        'assettools.AssetToolsProvide',
        on_delete=models.CASCADE,
        verbose_name='request provide of employee',
        related_name='provide_map_delivery',
    )
    provide_data = models.JSONField(
        default=dict,
        verbose_name='request provide of employee data',
        help_text=json.dumps(
            [
                {'id': '', 'title': '', 'code': ''}
            ]
        )
    )
    remark = models.CharField(
        verbose_name='Descriptions',
        max_length=500,
        null=True,
    )

    def create_backup_data(self):
        pass

    def before_save(self):
        self.create_backup_data()

    def save(self, *args, **kwargs):
        self.before_save()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Asset, Tools Delivery'
        verbose_name_plural = 'Asset, Tools Delivery'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class ProductDeliveredMapProvide(SimpleAbstractModel):
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        verbose_name='Product provide map with request delivery',
        related_name='product_in',
    )