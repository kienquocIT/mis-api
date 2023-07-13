from django.db import models
from django.utils import timezone
from apps.shared import SimpleAbstractModel


class OpportunityCallLog(SimpleAbstractModel):
    subject = models.CharField(max_length=250)
    opportunity = models.ForeignKey(
        'opportunity.Opportunity',
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
    input_result = models.CharField(max_length=250, null=True)
    repeat = models.BooleanField(default=False)
    date_created = models.DateTimeField(
        default=timezone.now, editable=False,
        help_text='The record created at value',
    )

    class Meta:
        verbose_name = 'OpportunityCallLog'
        verbose_name_plural = 'OpportunitiesCallLogges'
        ordering = ('call_date', 'date_created')
        default_permissions = ()
        permissions = ()


class OpportunityEmail(SimpleAbstractModel):
    opportunity = models.ForeignKey(
        'opportunity.Opportunity',
        on_delete=models.CASCADE,
        related_name="opportunity_send_email",
    )
    subject = models.CharField(max_length=250)
    email_to = models.CharField(max_length=250)
    email_to_contact = models.ForeignKey(
        'saledata.Contact',
        on_delete=models.CASCADE,
        related_name="opportunity_email_contact",
        null=True
    )
    email_cc_list = models.JSONField(default=list)
    content = models.CharField(max_length=500, null=True)
    date_created = models.DateTimeField(
        default=timezone.now, editable=False,
        help_text='The record created at value',
    )

    class Meta:
        verbose_name = 'OpportunityEmail'
        verbose_name_plural = 'OpportunitiesEmails'
        ordering = ('date_created',)
        default_permissions = ()
        permissions = ()
