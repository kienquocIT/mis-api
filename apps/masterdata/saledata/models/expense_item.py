from django.db import models

from apps.accounting.accountingsettings.utils.dimension_utils import DimensionUtils
from apps.shared import MasterDataAbstractModel

__all__ = ['ExpenseItem']


class ExpenseItem(MasterDataAbstractModel):
    description = models.CharField(
        max_length=1000,
        null=True,
        blank=True,
    )
    expense_parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        related_name='expense_child'
    )

    level = models.SmallIntegerField(
        default=0
    )
    is_parent = models.BooleanField(
        default=False,
        help_text='check instance has expense child'
    )

    class Meta:
        verbose_name = 'ExpenseItem'
        verbose_name_plural = 'ExpenseItems'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

    @classmethod
    def get_field_mapping(cls):
        return {
            'title': 'title',
            'code': 'code'
        }

    @classmethod
    def get_app_id(cls, raise_exception=True) -> str or None:
        return '245e9f47-df59-4d4a-b355-7eff2859247f'

    def save(self, *args, **kwargs):
        is_create = self._state.adding  # Check if is creating new record?
        # hit DB
        super().save(*args, **kwargs)

        DimensionUtils.sync_dimension_value(
            instance=self,
            app_id=self.__class__.get_app_id(),
            title=self.title,
            code=self.code,
            is_create=is_create
        )
