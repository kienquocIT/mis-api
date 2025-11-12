from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.shared import MasterDataAbstractModel

ACCOUNT_DIMENSION_TYPE = [
    (0, _("Required")),
    (1, _("Optional")),
]

__all__ = [
    'DimensionSyncConfig',
    'Dimension',
    'DimensionValue',
    'AccountDimensionMap'
]

class DimensionSyncConfig(MasterDataAbstractModel):
    related_app = models.ForeignKey(
        'base.Application',
        null=True,
        on_delete=models.SET_NULL,
        help_text='For example: set auto sync dimension for Account masterdata'
    )
    sync_on_create = models.BooleanField(default=False)
    sync_on_update = models.BooleanField(default=False)
    sync_on_delete = models.BooleanField(default=False)
    dimension = models.OneToOneField(
        'Dimension',
        on_delete=models.CASCADE,
        related_name='sync_config'
    )

    class Meta:
        verbose_name = 'Dimension Sync Config'
        verbose_name_plural = 'Dimension Sync Configs'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    def save(self, *args, **kwargs):

        super().save(*args, **kwargs)

        #auto update dimension related app when save config
        if self.dimension:
            self.dimension.related_app = self.related_app
            self.dimension.save(update_fields=['related_app'])


class Dimension(MasterDataAbstractModel):
    related_app = models.ForeignKey(
        'base.Application',
        null=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        verbose_name = 'Dimension Definition'
        verbose_name_plural = 'Dimension Definitions'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class DimensionValue(MasterDataAbstractModel):
    dimension = models.ForeignKey(
        'Dimension',
        on_delete=models.CASCADE,
        related_name='dimension_values',
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="child_values",
        verbose_name="",
        null=True,
    )
    allow_posting = models.BooleanField()
    relate_doc_id = models.UUIDField(null=True, help_text='uuid of the related model record')
    related_app = models.ForeignKey(
        'base.Application',
        null=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        verbose_name = 'Dimension Value'
        verbose_name_plural = 'Dimension Value'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class AccountDimensionMap(MasterDataAbstractModel):
    dimension = models.ForeignKey(
        'Dimension',
        on_delete=models.CASCADE,
        related_name='map_finance_accounts',
    )
    account = models.ForeignKey(
        'ChartOfAccounts',
        on_delete=models.CASCADE,
        related_name='map_dimensions',
    )
    status = models.IntegerField(choices=ACCOUNT_DIMENSION_TYPE, default=0)

    class Meta:
        verbose_name = 'Account Dimension Map'
        verbose_name_plural = 'Account Dimension Maps'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()
