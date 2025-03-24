from django.db import models

from django.utils.translation import gettext_lazy as _

from apps.shared import DataAbstractModel, SimpleAbstractModel

ORDER_STATUS_TYPE_CHOICES = [
    (1, _('Open')),
    (0, _('Close')),
]

class GroupOrder(DataAbstractModel):
    service_start_date = models.DateField()
    service_end_date = models.DateField()
    service_created_date = models.DateField()
    max_guest = models.PositiveIntegerField(default=0)
    registered_guest = models.PositiveIntegerField(default=0)
    order_status = models.SmallIntegerField(
        default=1,
        choices=ORDER_STATUS_TYPE_CHOICES
    )
    payment_term = models.ForeignKey(
        'saledata.PaymentTerm',
        on_delete=models.SET_NULL,
        related_name="payment_term_group_orders",
        null=True
    )
    cost_per_guest = models.FloatField(default=0)
    cost_per_registered_guest = models.FloatField(default=0)
    planned_revenue = models.FloatField(default=0)
    actual_revenue = models.FloatField(default=0)

    class Meta:
        verbose_name = _('Group Order')
        verbose_name_plural = _('Group Orders')
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()

class GroupOrderCustomer(SimpleAbstractModel):
    group_order = models.ForeignKey(
        'GroupOrder',
        on_delete=models.CASCADE,
        related_name='group_order_customers',
    )
