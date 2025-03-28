from django.db import models

from django.utils.translation import gettext_lazy as _

from apps.shared import DataAbstractModel, SimpleAbstractModel

__all__ = [
    'InstrumentTool',
    'InstrumentToolUseDepartment',
    'InstrumentToolSource',
    'InstrumentToolAPInvoiceItems'
]

INSTRUMENT_TOOL_STATUS = [
    (0, _('Using')),
    (1, _('Leased')),
    (2, _('Delivered')),
    (3, _('Under Maintenance')),
    (4, _('Fully Depreciated')),
]

SOURCE_TYPE_CHOICES = [
    (0, _('New Purchase')),
    (1, _('Financial Lease')),
    (2, _('Taken from Goods, Finished Products')),
    (3, _('Capital Construction Investment')),
    (4, _('Capital Contribution, Sponsorship, Donation')),
    (5, _('Exchange')),
]

TRANSACTION_TYPE_CHOICES = [
    (0, _('AP Invoice')),
    (1, _('Journal Entry')),
]


class InstrumentTool(DataAbstractModel):
    asset_code = models.CharField(max_length=100, blank=True)
    classification = models.ForeignKey(
        'saledata.ToolClassification',
        on_delete=models.CASCADE,
        related_name="classification_instrument_tools",
        null=True
    )
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        related_name="product_instrument_tools",
        null=True
    )
    manage_department = models.ForeignKey(
        'hr.Group',
        on_delete=models.SET_NULL,
        related_name="department_instrument_tools",
        null=True
    )
    use_customer = models.ForeignKey(
        'saledata.Account',
        on_delete=models.SET_NULL,
        related_name="account_instrument_tools",
        null=True
    )
    status = models.PositiveSmallIntegerField(
        default=0,
        choices=INSTRUMENT_TOOL_STATUS,
    )
    source_type = models.PositiveSmallIntegerField(
        default=0,
        choices=SOURCE_TYPE_CHOICES,
    )

    #depreciation + value:
    unit_price = models.FloatField(default=0)
    total_value = models.FloatField(default=0)
    quantity = models.IntegerField(default=0)
    measure_unit = models.CharField(max_length=150)
    depreciation_time = models.PositiveIntegerField(default=0)
    depreciation_time_unit = models.PositiveSmallIntegerField(
        default=0,
        choices=[
            (0, _('Month')),
            (1, _('Year')),
        ],
    )
    depreciation_start_date = models.DateTimeField()
    depreciation_end_date = models.DateTimeField()

    depreciation_data = models.JSONField(default=list, help_text='data for depreciation')

    # công cụ dụng cụ đã cấp phát
    allocated_quantity = models.PositiveIntegerField(
        default=0,
        help_text='quantity of allocated instruments and tools'
    )

    class Meta:
        verbose_name = 'Instrument Tool'
        verbose_name_plural = 'Instrument Tools'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    def save(self, *args, **kwargs):
        if self.system_status in [2, 3]:
            if not self.code:
                self.add_auto_generate_code_to_instance(self, 'IT[n4]', True)

                if 'update_fields' in kwargs:
                    if isinstance(kwargs['update_fields'], list):
                        kwargs['update_fields'].append('code')
                else:
                    kwargs.update({'update_fields': ['code']})

        # hit DB
        super().save(*args, **kwargs)

class InstrumentToolUseDepartment(SimpleAbstractModel):
    instrument_tool = models.ForeignKey(
        'asset.InstrumentTool',
        on_delete=models.CASCADE,
        related_name="use_departments",
        null=True
    )
    use_department = models.ForeignKey(
        'hr.Group',
        on_delete=models.CASCADE,
        related_name="instrument_tools",
        null=True
    )


class InstrumentToolSource(SimpleAbstractModel):
    instrument_tool = models.ForeignKey(
        'asset.InstrumentTool',
        on_delete=models.SET_NULL,
        related_name="asset_sources",
        null=True
    )
    description = models.CharField(max_length=150)
    document_no = models.CharField(max_length=150)
    transaction_type = models.PositiveSmallIntegerField(
        default=0,
        choices=TRANSACTION_TYPE_CHOICES,
    )
    code = models.CharField(max_length=150)
    value = models.FloatField()


class InstrumentToolAPInvoiceItems(SimpleAbstractModel):
    instrument_tool = models.ForeignKey(
        'asset.InstrumentTool',
        on_delete=models.SET_NULL,
        related_name="ap_invoice_items",
        null=True
    )
    ap_invoice_item = models.ForeignKey(
        'apinvoice.APInvoiceItems',
        on_delete=models.SET_NULL,
        related_name="instrument_tools",
        null=True
    )
    increased_FA_value = models.FloatField(default=0)
