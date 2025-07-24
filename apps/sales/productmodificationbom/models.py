from django.db import models
from apps.core.company.models import CompanyFunctionNumber
from apps.shared import SimpleAbstractModel, DataAbstractModel


class ProductModificationBOM(DataAbstractModel):
    product_mapped = models.ForeignKey('saledata.Product', on_delete=models.CASCADE, related_name='product_mapped')
    product_mapped_data = models.JSONField(default=dict)
    base_cost = models.FloatField(default=0)
    modified_cost = models.FloatField(default=0)

    def save(self, *args, **kwargs):
        if self.system_status in [2, 3]:  # added, finish
            if isinstance(kwargs['update_fields'], list):
                if 'date_approved' in kwargs['update_fields']:
                    CompanyFunctionNumber.auto_gen_code_based_on_config(
                        'productmodificationbom', True, self, kwargs
                    )

        # hit DB
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Product Modification'
        verbose_name_plural = 'Product Modification'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class PMBOMCurrentComponent(SimpleAbstractModel):
    product_modified_bom = models.ForeignKey(
        ProductModificationBOM, on_delete=models.CASCADE, related_name='current_components'
    )
    order = models.IntegerField(default=1)
    component_text_data = models.JSONField(default=dict) # {'title': ...; 'description':...}
    base_quantity = models.FloatField()
    removed_quantity = models.FloatField(default=0)
    cost = models.FloatField(default=0)
    subtotal = models.FloatField(default=0)

    class Meta:
        verbose_name = 'PM BOM Current Component'
        verbose_name_plural = 'PM BOM Current Components'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


class PMBOMAddedComponent(SimpleAbstractModel):
    product_modified_bom = models.ForeignKey(
        ProductModificationBOM, on_delete=models.CASCADE, related_name='added_components'
    )
    order = models.IntegerField(default=1)
    product_added = models.ForeignKey('saledata.Product', on_delete=models.CASCADE, related_name='product_added')
    product_added_data = models.JSONField(default=dict)
    added_quantity = models.FloatField(default=0)
    cost = models.FloatField(default=0)
    subtotal = models.FloatField(default=0)

    class Meta:
        verbose_name = 'PM BOM Added Component'
        verbose_name_plural = 'PM BOM Added Components'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()
