__all__ = ['WorkMapExpense']

from django.db import models
from apps.shared import DataAbstractModel


class WorkMapExpense(DataAbstractModel):
    work = models.ForeignKey(
        'project.ProjectWorks',
        on_delete=models.CASCADE,
        related_name='%(app_label)s_%(class)s_work',
    )
    expense_item = models.ForeignKey(
        'saledata.ExpenseItem',
        on_delete=models.CASCADE,
        related_name='%(app_label)s_%(class)s_expense_item',
    )
    expense_name = models.ForeignKey(
        'saledata.Expense',
        on_delete=models.SET_NULL,
        related_name='%(app_label)s_%(class)s_expense_name',
        null=True
    )
    uom = models.ForeignKey(
        'saledata.UnitOfMeasure',
        on_delete=models.CASCADE,
        verbose_name="Unit of Measure",
        related_name='%(app_label)s_%(class)s_uom',
    )
    quantity = models.SmallIntegerField(
        help_text='quantity of expense'
    )
    expense_price = models.FloatField(
        help_text='price of expense'
    )
    tax = models.ForeignKey(
        'saledata.Tax',
        on_delete=models.CASCADE,
        verbose_name="Tax",
        help_text="Tax per record",
        related_name='%(app_label)s_%(class)s_tax',
    )
    sub_total = models.FloatField(
        help_text='total price per record (expense_price * quantity)'
    )
    sub_total_after_tax = models.FloatField(
        help_text='total price per record after tax (sub_total + (expense_price * tax / 100) )'
    )
    is_labor = models.BooleanField(
        default=False,
        help_text='flag to know this record is labor or not',
    )
