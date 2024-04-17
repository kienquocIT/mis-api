from django.db import models

from apps.shared import MasterDataAbstractModel, SimpleAbstractModel, StringHandler

__all__ = ['PaymentTerm', 'Term']


APPLY_FOR_CHOICES = (
    (0, 'Sale'),
    (1, 'Purchase'),
)


class PaymentTerm(MasterDataAbstractModel):
    code = models.CharField(max_length=100)
    apply_for = models.IntegerField(default=0, choices=APPLY_FOR_CHOICES, help_text='Applicable subjects')
    remark = models.CharField(verbose_name='Descriptions', max_length=250, blank=True, null=True)
    term = models.JSONField(
        verbose_name="Term",
        default=list,
        help_text="Term JSON string data"
    )

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = StringHandler.random_str(10, 2)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Payment Term'
        verbose_name_plural = 'Payment Term'
        unique_together = ('company', 'code')
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


UNIT_TYPE_CHOICES = (
    (0, 'Percent'),
    (1, 'Amount'),
    (2, 'Balance'),
)

DAY_TYPE_CHOICES = (
    (1, 'Workday'),
    (2, 'Calendar day')
)

TRIGGER_ACTION_CHOICES = (
    (0, ''),
    (1, 'Contract date'),
    (2, 'Delivery date'),
    (3, 'Invoice date'),
    (4, 'Acceptance date'),
    (5, 'End of invoice month'),
    (6, 'Order date'),
)


class Term(SimpleAbstractModel):
    unit_type = models.IntegerField(
        verbose_name='Unit type', default=0,
        choices=UNIT_TYPE_CHOICES,
        help_text='Value calculation rules for value fields',
    )
    value = models.CharField(
        verbose_name='Value', max_length=50, help_text='This value using with unit_type'
    )
    day_type = models.IntegerField(
        verbose_name='Day type', default=0,
        choices=DAY_TYPE_CHOICES,
        help_text='The day calculation rule ends with the value no_of_days',
    )
    no_of_days = models.CharField(
        verbose_name='Number of days', max_length=30, help_text='Amount of days from after is activated'
    )
    after = models.IntegerField(
        verbose_name='After', default=0,
        choices=TRIGGER_ACTION_CHOICES,
        help_text='This value using with no_of_days. Terms available with these conditions when it is activated'
    )
    payment_term = models.ForeignKey(
        PaymentTerm,
        on_delete=models.CASCADE,
        verbose_name="Payment term",
        related_name="term_payment_term",
        null=True
    )
    order = models.IntegerField(
        default=1, help_text='Order number of the term list in the payment term'
    )

    class Meta:
        verbose_name = 'Term'
        verbose_name_plural = 'Term'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()
