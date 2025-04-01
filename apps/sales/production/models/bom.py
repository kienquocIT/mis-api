from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.sales.cashoutflow.utils import AdvanceHandler
from apps.shared import DataAbstractModel, MasterDataAbstractModel

BOM_TYPE = [
    (0, _('For production')),
    (1, _('For service')),
    (2, _('For sale')),
    (3, _('For internal expense')),
    (4, _('For opportunity'))
]


class BOM(DataAbstractModel):
    bom_type = models.SmallIntegerField(choices=BOM_TYPE, default=0)
    for_outsourcing = models.BooleanField(default=False)
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        related_name='bom_product'
    )
    product_data = models.JSONField(default=dict)
    sum_price = models.FloatField(default=0)
    sum_time = models.FloatField(default=0)

    opportunity = models.ForeignKey(
        'opportunity.Opportunity',
        on_delete=models.CASCADE,
        null=True,
        related_name='bom_opportunity'
    )
    opp_data = models.JSONField(default=dict)

    class Meta:
        verbose_name = 'Bill of material'
        verbose_name_plural = 'Bills of material'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    @classmethod
    def check_change_document(cls, instance):
        if not instance:
            return False
        return True

    @classmethod
    def check_reject_document(cls, instance):
        if not instance:
            return False
        return True

    def save(self, *args, **kwargs):
        if self.system_status in [2, 3]:
            if not self.code:
                self.add_auto_generate_code_to_instance(self, 'BOM[n4]', False)

                if 'update_fields' in kwargs:
                    if isinstance(kwargs['update_fields'], list):
                        kwargs['update_fields'].append('code')
                else:
                    kwargs.update({'update_fields': ['code']})

                if self.product.has_bom:
                    raise ValueError("This product is mapped with BOM")
                self.product.has_bom = True
                self.product.bom_data = {
                    'id': str(self.id),
                    'code': self.code,
                    'title': self.title,
                    'bom_type': self.bom_type,
                    'for_outsourcing': self.for_outsourcing,
                    'sum_price': self.sum_price,
                    'sum_time': self.sum_time,
                    'opp_data': self.opp_data,
                }
                self.product.save(update_fields=['has_bom', 'bom_data'])

        # opportunity log
        AdvanceHandler.push_opportunity_log(instance=self)

        # hit DB
        super().save(*args, **kwargs)


# Standard
class BOMProcess(MasterDataAbstractModel):
    bom = models.ForeignKey(
        BOM,
        on_delete=models.CASCADE,
        related_name='bom_process_bom'
    )
    order = models.IntegerField(default=1)
    task_name = models.CharField(max_length=250)
    labor = models.ForeignKey(
        'saledata.Expense',
        on_delete=models.CASCADE,
        related_name='bom_process_labor'
    )
    quantity = models.FloatField(default=0)
    uom = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        related_name='bom_process_uom'
    )
    uom_data = models.JSONField(default=dict)
    unit_price = models.FloatField(default=0)
    subtotal_price = models.FloatField(default=0)
    note = models.TextField()

    class Meta:
        verbose_name = 'BOM process'
        verbose_name_plural = 'BOM processes'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


class BOMSummaryProcess(MasterDataAbstractModel):
    bom = models.ForeignKey(
        BOM,
        on_delete=models.CASCADE,
        related_name='bom_summary_process_bom'
    )
    order = models.IntegerField(default=1)
    labor = models.ForeignKey(
        'saledata.Expense',
        on_delete=models.CASCADE,
        related_name='bom_summary_process_labor'
    )
    labor_data = models.JSONField(default=dict)
    quantity = models.FloatField(default=0)
    uom = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        related_name='bom_summary_process_uom'
    )
    uom_data = models.JSONField(default=dict)
    unit_price = models.FloatField(default=0)
    subtotal_price = models.FloatField(default=0)

    class Meta:
        verbose_name = 'BOM summary process'
        verbose_name_plural = 'BOM summary processes'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


class BOMMaterialComponent(MasterDataAbstractModel):
    bom = models.ForeignKey(
        BOM,
        on_delete=models.CASCADE,
        related_name='bom_material_component_bom'
    )
    bom_process = models.ForeignKey(
        BOMProcess,
        on_delete=models.CASCADE,
        related_name='bom_material_component_bom_process',
        null=True
    )
    bom_process_order = models.IntegerField(default=1)
    order = models.IntegerField(default=1)
    material = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        related_name='bom_material_component_material'
    )
    material_data = models.JSONField(default=dict)
    quantity = models.FloatField(default=0)
    standard_price = models.FloatField(default=0)
    subtotal_price = models.FloatField(default=0)
    uom = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        related_name='bom_material_component_uom'
    )
    uom_data = models.JSONField(default=dict)
    disassemble = models.BooleanField(default=False)
    note = models.TextField()
    replacement_data = models.JSONField(default=list)
    for_outsourcing = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'BOM material component'
        verbose_name_plural = 'BOM materials components'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()


class BOMReplacementMaterialComponent(MasterDataAbstractModel):
    bom = models.ForeignKey(
        BOM,
        on_delete=models.CASCADE,
        related_name='bom_replacement_material_component_bom'
    )
    material = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        related_name='bom_replacement_material_component_material'
    )
    material_data = models.JSONField(default=dict)
    quantity = models.FloatField(default=0)
    uom = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        related_name='bom_replacement_material_component_uom'
    )
    uom_data = models.JSONField(default=dict)
    disassemble = models.BooleanField(default=False)
    note = models.TextField()
    replace_for = models.ForeignKey(
        BOMMaterialComponent,
        on_delete=models.CASCADE,
        null=True,
        related_name='bom_replacement_material_replace_for'
    )

    class Meta:
        verbose_name = 'BOM replacement material component'
        verbose_name_plural = 'BOM replacement materials components'
        ordering = ()
        default_permissions = ()
        permissions = ()


class BOMTool(MasterDataAbstractModel):
    bom = models.ForeignKey(
        BOM,
        on_delete=models.CASCADE,
        related_name='bom_tool_bom'
    )
    bom_process = models.ForeignKey(
        BOMProcess,
        on_delete=models.CASCADE,
        related_name='bom_tool_bom_process'
    )
    bom_process_order = models.IntegerField(default=1)
    order = models.IntegerField(default=1)
    tool = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        related_name='bom_tool_tool'
    )
    tool_data = models.JSONField(default=dict)
    quantity = models.FloatField(default=0)
    uom = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        related_name='bom_tool_uom'
    )
    uom_data = models.JSONField(default=dict)
    note = models.TextField()

    class Meta:
        verbose_name = 'BOM tool'
        verbose_name_plural = 'BOM tools'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()
