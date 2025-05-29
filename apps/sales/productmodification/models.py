from django.db import models
from apps.shared import SimpleAbstractModel, DataAbstractModel


class ProductModification(DataAbstractModel):
    product_modified = models.ForeignKey('saledata.Product', on_delete=models.CASCADE, related_name='product_modified')
    product_modified_data = models.JSONField(default=dict)

    prd_wh = models.ForeignKey('saledata.ProductWareHouse', on_delete=models.CASCADE, null=True)

    prd_wh_lot = models.ForeignKey('saledata.ProductWareHouseLot', on_delete=models.CASCADE, null=True)
    prd_wh_lot_data = models.JSONField(default=dict)

    prd_wh_serial = models.ForeignKey('saledata.ProductWareHouseSerial', on_delete=models.CASCADE, null=True)
    prd_wh_serial_data = models.JSONField(default=dict)

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


class CurrentComponent(SimpleAbstractModel):
    product_modified = models.ForeignKey(
        ProductModification, on_delete=models.CASCADE, related_name='current_components'
    )
    order = models.IntegerField(default=1)
    component_text_data = models.JSONField(default=dict)
    component_product = models.ForeignKey('saledata.Product', on_delete=models.CASCADE, null=True)
    component_product_data = models.JSONField(default=dict)
    component_quantity = models.IntegerField()

    class Meta:
        verbose_name = 'Current Component'
        verbose_name_plural = 'Current Components'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()

class CurrentComponentDetail(SimpleAbstractModel):
    product_modified = models.ForeignKey(
        ProductModification, on_delete=models.CASCADE, related_name='current_components_detail'
    )

    component_prd_wh = models.ForeignKey(
        'saledata.ProductWareHouse', on_delete=models.CASCADE, null=True
    )
    component_prd_wh_quantity = models.FloatField(default=0)

    component_prd_wh_lot = models.ForeignKey(
        'saledata.ProductWareHouseLot', on_delete=models.CASCADE, null=True
    )
    component_prd_wh_lot_data = models.JSONField(default=dict)
    component_prd_wh_lot_quantity = models.FloatField(default=0)

    component_prd_wh_serial = models.ForeignKey(
        'saledata.ProductWareHouseSerial', on_delete=models.CASCADE, null=True
    )
    component_prd_wh_serial_data = models.JSONField(default=dict)

    class Meta:
        verbose_name = 'Current Component Detail'
        verbose_name_plural = 'Current Components Detail'
        default_permissions = ()
        permissions = ()


class RemovedComponent(SimpleAbstractModel):
    product_modified = models.ForeignKey(
        ProductModification, on_delete=models.CASCADE, related_name='removed_components'
    )
    order = models.IntegerField(default=1)
    component_text_data = models.JSONField(default=dict)
    component_product = models.ForeignKey('saledata.Product', on_delete=models.CASCADE, null=True)
    component_product_data = models.JSONField(default=dict)
    component_quantity = models.IntegerField()

    class Meta:
        verbose_name = 'Removed Component'
        verbose_name_plural = 'Removed Components'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


class RemovedComponentDetail(SimpleAbstractModel):
    product_modified = models.ForeignKey(
        ProductModification, on_delete=models.CASCADE, related_name='removed_components_detail'
    )

    component_prd_wh = models.ForeignKey(
        'saledata.ProductWareHouse', on_delete=models.CASCADE, null=True
    )
    component_prd_wh_quantity = models.FloatField(default=0)

    component_prd_wh_lot = models.ForeignKey(
        'saledata.ProductWareHouseLot', on_delete=models.CASCADE, null=True
    )
    component_prd_wh_lot_data = models.JSONField(default=dict)
    component_prd_wh_lot_quantity = models.FloatField(default=0)

    component_prd_wh_serial = models.ForeignKey(
        'saledata.ProductWareHouseSerial', on_delete=models.CASCADE, null=True
    )
    component_prd_wh_serial_data = models.JSONField(default=dict)

    class Meta:
        verbose_name = 'Removed Component Detail'
        verbose_name_plural = 'Removed Components Detail'
        default_permissions = ()
        permissions = ()
