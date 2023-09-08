from django.db import models
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
