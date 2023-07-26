import uuid

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
        ordering = ('-call_date', '-date_created')
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
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class OpportunityMeeting(SimpleAbstractModel):
    subject = models.CharField(max_length=250)
    opportunity = models.ForeignKey(
        'opportunity.Opportunity',
        on_delete=models.CASCADE,
        related_name="opportunity_meeting",
    )
    employee_attended_list = models.ManyToManyField(
        'hr.Employee',
        through='OpportunityMeetingEmployeeAttended',
        symmetrical=False,
        related_name='all_employee_attended'
    )
    customer_member_list = models.ManyToManyField(
        'saledata.Contact',
        through='OpportunityMeetingCustomerMember',
        symmetrical=False,
        related_name='all_customer_member'
    )
    meeting_date = models.DateTimeField()
    meeting_address = models.CharField(max_length=250)
    room_location = models.CharField(max_length=250, null=True)
    input_result = models.CharField(max_length=250, null=True)
    repeat = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'OpportunityMeeting'
        verbose_name_plural = 'OpportunitiesMeetings'
        ordering = ('-meeting_date',)
        default_permissions = ()
        permissions = ()


class OpportunityMeetingEmployeeAttended(SimpleAbstractModel):
    meeting_mapped = models.ForeignKey(OpportunityMeeting, on_delete=models.CASCADE)
    employee_attended_mapped = models.ForeignKey('hr.Employee', on_delete=models.CASCADE)


class OpportunityMeetingCustomerMember(SimpleAbstractModel):
    meeting_mapped = models.ForeignKey(OpportunityMeeting, on_delete=models.CASCADE)
    customer_member_mapped = models.ForeignKey('saledata.Contact', on_delete=models.CASCADE)


class OpportunityDocument(SimpleAbstractModel):
    subject = models.CharField(max_length=250)
    opportunity = models.ForeignKey(
        'opportunity.Opportunity',
        on_delete=models.CASCADE,
        related_name="opportunity_document",
    )
    request_completed_date = models.DateTimeField()
    kind_of_product = models.CharField(max_length=250)
    person_in_charge = models.ManyToManyField(
        'hr.Employee',
        through='OpportunityDocumentPersonInCharge',
        symmetrical=False,
        related_name='opp_document_map_employees',
    )
    data_documents = models.JSONField(
        default=list,
    )

    class Meta:
        verbose_name = 'OpportunityDocument'
        verbose_name_plural = 'OpportunityDocuments'
        ordering = ()
        default_permissions = ()
        permissions = ()


class OpportunityDocumentPersonInCharge(SimpleAbstractModel):
    document = models.ForeignKey(
        OpportunityDocument,
        on_delete=models.CASCADE,
        related_name="opportunity_document_1",
    )

    person = models.ForeignKey(
        'hr.Employee',
        on_delete=models.CASCADE,
        related_name="person",
    )

    class Meta:
        verbose_name = 'OpportunityDocumentPersonInCharge'
        verbose_name_plural = 'OpportunityDocumentPersonsInCharge'
        ordering = ()
        default_permissions = ()
        permissions = ()


class OpportunitySubDocument(SimpleAbstractModel):
    document = models.ForeignKey(
        OpportunityDocument,
        on_delete=models.CASCADE,
        related_name="opportunity_document",
    )

    attachment = models.OneToOneField(
        'attachments.Files',
        on_delete=models.CASCADE,
        verbose_name='Sub Opportunity document attachment files',
        help_text='Sub Opportunity document had one/many attachment file',
        related_name='sub_document_attachment_file',
    )
    media_file = models.UUIDField(unique=True, default=uuid.uuid4)

    description = models.CharField(max_length=1000)

    class Meta:
        verbose_name = 'OpportunitySubDocument'
        verbose_name_plural = 'OpportunitySubsDocument'
        ordering = ()
        default_permissions = ()
        permissions = ()
