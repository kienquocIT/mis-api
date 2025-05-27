from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.shared import SimpleAbstractModel, DataAbstractModel


class ProductModification(DataAbstractModel):
    product_modified = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        related_name='product_modified'
    )
    product_modified_data = models.JSONField(default=dict)
    product_warehouse = models.ForeignKey(
        'saledata.ProductWareHouse',
        on_delete=models.CASCADE,
        related_name='product_modified_product_warehouse'
    )
    product_warehouse_lot = models.ForeignKey(
        'saledata.ProductWareHouseLot',
        on_delete=models.CASCADE,
        null=True,
        related_name='product_modified_product_warehouse_lot'
    )
    product_warehouse_lot_data = models.JSONField(default=dict)
    product_warehouse_serial = models.ForeignKey(
        'saledata.ProductWareHouseSerial',
        on_delete=models.CASCADE,
        null=True,
        related_name='product_modified_product_warehouse_serial'
    )
    product_warehouse_serial_data = models.JSONField(default=dict)
    detail_product_modified_info = models.CharField(max_length=200, null=True, default='')

    def save(self, *args, **kwargs):
        if self.system_status in [2, 3]:
            if not self.code:
                self.add_auto_generate_code_to_instance(self, 'PM[n4]', True)
                if 'update_fields' in kwargs:
                    if isinstance(kwargs['update_fields'], list):
                        kwargs['update_fields'].append('code')
                else:
                    kwargs.update({'update_fields': ['code']})
        # hit DB
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Product Modification'
        verbose_name_plural = 'Product Modification'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
