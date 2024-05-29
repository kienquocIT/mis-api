from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.shared import SimpleAbstractModel, DataAbstractModel


TOTAL_EMPLOYEES_SELECTION = [
    (1, _('< 20 people')),
    (2, _('20-50 people')),
    (3, _('50-200 people')),
    (4, _('200-500 people')),
    (5, _('> 500 people'))
]
ANNUAL_REVENUE_SELECTION = [
    (1, _('1-10 billions')),
    (2, _('10-20 billions')),
    (3, _('20-50 billions')),
    (4, _('50-200 billions')),
    (5, _('200-1000 billions')),
    (6, _('> 1000 billions'))
]
LEAD_SOURCE = [
    (0, _('Manual'))
]
LEAD_STATUS = [
    (1, _('Prospect')),
    (2, _('Open - not contacted')),
    (3, _('Working')),
    (4, _('Opportunity created')),
    (5, _('Not a target'))
]


class Lead(DataAbstractModel):
    contact_name = models.CharField(max_length=200, blank=True)
    job_title = models.CharField(max_length=200, blank=True)
    mobile = models.CharField(max_length=200, blank=True)
    email = models.CharField(max_length=200, blank=True)
    company_name = models.CharField(max_length=200, blank=True)
    account_name = models.CharField(max_length=200, blank=True)
    industry = models.ForeignKey('saledata.Industry', on_delete=models.SET_NULL, null=True)
    total_employees = models.SmallIntegerField(
        choices=TOTAL_EMPLOYEES_SELECTION,
        verbose_name='total employees of account in lead',
        null=True
    )
    revenue = models.SmallIntegerField(
        choices=ANNUAL_REVENUE_SELECTION,
        verbose_name='annual revenue of account in lead',
        blank=True,
        null=True
    )
    source = models.SmallIntegerField(choices=LEAD_SOURCE, default=0)
    lead_status = models.SmallIntegerField(choices=LEAD_STATUS, default=0)
    assign_to_sale = models.ForeignKey('hr.Employee', on_delete=models.SET_NULL, null=True)
    current_lead_stage = models.ForeignKey('lead.LeadStage', on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = 'Lead'
        verbose_name_plural = 'Leads'
        ordering = ('-date_created',)
        default_permissions = ()
        permissions = ()


class LeadNote(SimpleAbstractModel):
    lead = models.ForeignKey('lead.Lead', on_delete=models.CASCADE, related_name='lead_notes')
    note = models.CharField(max_length=250, blank=True)

    class Meta:
        verbose_name = 'Lead note'
        verbose_name_plural = 'Lead notes'
        ordering = ()
        default_permissions = ()
        permissions = ()


class LeadStage(SimpleAbstractModel):
    tenant = models.ForeignKey('tenant.Tenant', on_delete=models.CASCADE)
    company = models.ForeignKey('company.Company', on_delete=models.CASCADE)
    stage_title = models.CharField(max_length=250)
    level = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Lead stage'
        verbose_name_plural = 'Lead stages'
        ordering = ('level',)
        default_permissions = ()
        permissions = ()


class LeadConfig(SimpleAbstractModel):
    lead = models.ForeignKey('lead.Lead', on_delete=models.CASCADE, related_name='lead_configs')
    create_contact = models.BooleanField(default=False)
    convert_opp = models.BooleanField(default=False)
    convert_opp_create = models.BooleanField(default=True)
    convert_opp_select = models.BooleanField(default=False)
    opp_select = models.ForeignKey('opportunity.Opportunity', on_delete=models.CASCADE, null=True)
    convert_account_create = models.BooleanField(default=True)
    convert_account_select = models.BooleanField(default=False)
    account_select = models.ForeignKey('saledata.Account', on_delete=models.CASCADE, null=True)
    assign_to_sale_config = models.ForeignKey('hr.Employee', on_delete=models.SET_NULL, null=True)

    contact_mapped = models.ForeignKey('saledata.Contact', on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = 'Lead config'
        verbose_name_plural = 'Lead configs'
        ordering = ()
        default_permissions = ()
        permissions = ()
