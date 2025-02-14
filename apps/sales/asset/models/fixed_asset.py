from django.db import models

from django.utils.translation import gettext_lazy as _

from apps.shared import DataAbstractModel, SimpleAbstractModel

__all__ = [
    'FixedAsset',
    'FixedAssetUseDepartment',
    'FixedAssetSource',
    'FixedAssetAPInvoiceItems'
]

FIXED_ASSET_STATUS = [
    (0, _('Using')),
    (1, _('Leased')),
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

DEPRECIATION_TYPE_CHOICES = [
    (0, _('Straight line depreciation')),
    (1, _('Adjusted reducing balance')),
]


class FixedAsset(DataAbstractModel):
    classification = models.ForeignKey(
        'saledata.FixedAssetClassification',
        on_delete=models.CASCADE,
        related_name="classification_fixed_assets",
        null=True
    )
    product = models.ForeignKey(
        'saledata.Product',
        on_delete=models.CASCADE,
        related_name="product_fixed_assets",
        null=True
    )
    manage_department = models.ForeignKey(
        'hr.Group',
        on_delete=models.SET_NULL,
        related_name="department_fixed_assets",
        null=True
    )
    use_customer = models.ForeignKey(
        'saledata.Account',
        on_delete=models.SET_NULL,
        related_name="account_fixed_assets",
        null=True
    )
    status = models.PositiveSmallIntegerField(
        default=0,
        choices=FIXED_ASSET_STATUS,
    )
    source_type = models.PositiveSmallIntegerField(
        default=0,
        choices=SOURCE_TYPE_CHOICES,
    )

    #depreciation + value:
    original_cost = models.FloatField(default=0)
    accumulative_depreciation = models.FloatField(default=0)
    net_book_value = models.FloatField(default=0)
    depreciation_method = models.PositiveSmallIntegerField(
        default=0,
        choices=DEPRECIATION_TYPE_CHOICES,
    )
    depreciation_time = models.PositiveIntegerField(default=0)
    depreciation_time_unit = models.PositiveSmallIntegerField(
        default=0,
        choices=[
            (0, _('Month')),
            (1, _('Year')),
        ],
    )
    adjustment_factor = models.FloatField(null=True)
    depreciation_start_date = models.DateTimeField()
    depreciation_end_date = models.DateTimeField()

    class Meta:
        verbose_name = 'Fixed Asset'
        verbose_name_plural = 'Fixed Assets'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    @classmethod
    def get_app_id(cls, raise_exception=True) -> str or None:
        return 'fc552ebb-eb98-4d7b-81cd-e4b5813b7815'  # fixed asset's application id


class FixedAssetUseDepartment(SimpleAbstractModel):
    fixed_asset = models.ForeignKey(
        'asset.FixedAsset',
        on_delete=models.CASCADE,
        related_name="use_departments",
        null=True
    )
    use_department = models.ForeignKey(
        'hr.Group',
        on_delete=models.CASCADE,
        related_name="fixed_assets",
        null=True
    )


class FixedAssetSource(SimpleAbstractModel):
    fixed_asset = models.ForeignKey(
        'asset.FixedAsset',
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


class FixedAssetAPInvoiceItems(SimpleAbstractModel):
    fixed_asset = models.ForeignKey(
        'asset.FixedAsset',
        on_delete=models.SET_NULL,
        related_name="ap_invoice_items",
        null=True
    )
    ap_invoice_item = models.ForeignKey(
        'apinvoice.APInvoiceItems',
        on_delete=models.SET_NULL,
        related_name="fixed_assets",
        null=True
    )
    increased_FA_value = models.FloatField(default=0)
