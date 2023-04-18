from . import models  # pylint: disable=C0413
from . import MasterDataAbstractModel, SimpleAbstractModel  # pylint: disable=C0413


class PaymentTerm(MasterDataAbstractModel):  # noqa
    apply_for = models.IntegerField(default=0)
    remark = models.CharField(verbose_name='Descriptions', max_length=250, blank=True, null=True)
    term = models.JSONField(
        verbose_name="Term",
        default=list,
        help_text="Term JSON string data"
    )

    class Meta:
        verbose_name = 'Payment Term'
        verbose_name_plural = 'Payment Term'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class Term(SimpleAbstractModel):
    value = models.CharField(verbose_name='Value', max_length=50)
    unit_type = models.IntegerField(verbose_name='Unit type', default=0)
    day_type = models.IntegerField(verbose_name='Day type', default=0)
    no_of_days = models.CharField(verbose_name='No of days', max_length=30)
    after = models.IntegerField(verbose_name='After', default=0)
    payment_term = models.ForeignKey(
        PaymentTerm,
        on_delete=models.CASCADE,
        verbose_name="Payment term",
        related_name="term_payment_term",
        null=True
    )
    order = models.IntegerField(default=1)

    class Meta:
        verbose_name = 'Term'
        verbose_name_plural = 'Term'
        ordering = ('order',)
        default_permissions = ()
        permissions = ()
