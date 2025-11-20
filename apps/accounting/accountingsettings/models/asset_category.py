from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.shared import MasterDataAbstractModel

CATEGORY_TYPE = [
    (0, _("Tangible Asset")),
    (1, _("Intangible Asset")),
    (2, _("Instrument and Tool")),
    (3, _("Prepaid Expense")),
]

DEPRECIATION_TYPE_CHOICES = [
    (0, _('Straight line depreciation')),
    (1, _('Adjusted reducing balance')),
]

class AssetCategory(MasterDataAbstractModel):
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        related_name='child_categories',
    )

    remark = models.TextField()
    category_type = models.IntegerField(choices=CATEGORY_TYPE, default=0)

    # depreciation setting
    depreciation_method = models.PositiveSmallIntegerField(
        default=0,
        choices=DEPRECIATION_TYPE_CHOICES,
    )
    depreciation_time = models.PositiveIntegerField(default=0)

    # account mapping
    asset_account = models.ForeignKey(
        'accountingsettings.ChartOfAccounts',
        on_delete=models.SET_NULL,
        null=True,
        related_name='+',
    )
    accumulated_depreciation_account = models.ForeignKey(
        'accountingsettings.ChartOfAccounts',
        on_delete=models.SET_NULL,
        null=True,
        related_name='+',
    )
    depreciation_expense_account = models.ForeignKey(
        'accountingsettings.ChartOfAccounts',
        on_delete=models.SET_NULL,
        null=True,
        related_name='+',
    )

    class Meta:
        verbose_name = _('Asset Category')
        verbose_name_plural = _('Asset Categories')
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
