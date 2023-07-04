from django.db import models
from apps.shared import SimpleAbstractModel
from .opportunity import Opportunity


class OpportunityCallLog(SimpleAbstractModel):
    subject = models.CharField(max_length=250)
    opportunity = models.ForeignKey(
        Opportunity,
        on_delete=models.CASCADE,
        related_name="opportunity_calllog",
    )
    customer = models.ForeignKey(
        'saledata.Account',
        on_delete=models.CASCADE,
        related_name="opportunity_calllog_customer",
    )
    contact = models.ForeignKey(
        'saledata.Contact',
        on_delete=models.CASCADE,
        related_name="opportunity_calllog_contact",
    )
    call_date = models.DateTimeField()
    result = models.CharField(max_length=250, null=True)
    repeat = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'OpportunityCallLog'
        verbose_name_plural = 'OpportunitiesCallLogges'
        ordering = ()
        default_permissions = ()
        permissions = ()
