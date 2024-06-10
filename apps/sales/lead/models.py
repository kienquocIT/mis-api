from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.masterdata.saledata.models.periods import Periods
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
    (5, _('Disqualified')),
    (6, _('Not a target'))
]


class Lead(DataAbstractModel):
    contact_name = models.CharField(max_length=200, blank=True)
    job_title = models.CharField(max_length=200, blank=True)
    mobile = models.CharField(max_length=200, blank=True)
    email = models.CharField(max_length=200, blank=True)
    company_name = models.CharField(max_length=200, blank=True)
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
    period_mapped = models.ForeignKey('saledata.Periods', on_delete=models.SET_NULL, null=True)

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
    account_mapped = models.ForeignKey(
        'saledata.Account', on_delete=models.CASCADE, null=True, related_name='lead_account_mapped'
    )
    assign_to_sale_config = models.ForeignKey(
        'hr.Employee', on_delete=models.SET_NULL, null=True, related_name='lead_assign_to_sale_config'
    )
    contact_mapped = models.ForeignKey(
        'saledata.Contact', on_delete=models.CASCADE, null=True, related_name='lead_contact_mapped'
    )
    opp_mapped = models.ForeignKey(
        'opportunity.Opportunity', on_delete=models.CASCADE, null=True, related_name='lead_opp_mapped'
    )

    class Meta:
        verbose_name = 'Lead config'
        verbose_name_plural = 'Lead configs'
        ordering = ()
        default_permissions = ()
        permissions = ()


class LeadChartInformation(SimpleAbstractModel):
    tenant = models.ForeignKey('tenant.Tenant', on_delete=models.CASCADE)
    company = models.ForeignKey('company.Company', on_delete=models.CASCADE)
    status_amount_information = models.JSONField(default=dict)
    stage_amount_information = models.JSONField(default=dict)
    period_mapped = models.ForeignKey('saledata.Periods', on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = 'Lead Chart Information'
        verbose_name_plural = 'Lead Charts Information'
        ordering = ()
        default_permissions = ()
        permissions = ()

    @classmethod
    def get_chart_information(cls, tenant_id, company_id, this_period):
        all_lead = Lead.objects.filter(
            tenant_id=tenant_id, company_id=company_id, period_mapped=this_period
        ).select_related('current_lead_stage')
        status_amount_information = {}
        stage_amount_information = {}
        for lead in all_lead:
            if lead.lead_status not in status_amount_information:
                status_amount_information[lead.lead_status] = 1
            else:
                status_amount_information[lead.lead_status] += 1

            if lead.current_lead_stage.stage_title not in stage_amount_information:
                stage_amount_information[lead.current_lead_stage.stage_title] = 1
            else:
                stage_amount_information[lead.current_lead_stage.stage_title] += 1

        new_status_amount_information = {}
        for status in LEAD_STATUS:
            amount = status_amount_information.get(int(status[0]))
            new_status_amount_information[str(status[1])] = amount if amount else 0

        new_stage_amount_information = {}
        for stage in LeadStage.objects.filter(tenant_id=tenant_id, company_id=company_id):
            amount = stage_amount_information.get(stage.stage_title)
            new_stage_amount_information[stage.stage_title] = {
                'amount': amount,
                'level': stage.level
            } if amount else {
                'amount': 0,
                'level': stage.level
            }

        return new_status_amount_information, new_stage_amount_information

    @classmethod
    def create_update_chart_information(cls, tenant_id, company_id):
        this_period = Periods.objects.filter(
            tenant_id=tenant_id, company_id=company_id, fiscal_year=timezone.now().year
        ).first()
        chart_info_obj = LeadChartInformation.objects.filter(
            tenant_id=tenant_id, company_id=company_id, period_mapped=this_period
        ).first()
        if this_period:
            status_amount_information, stage_amount_information = LeadChartInformation.get_chart_information(
                tenant_id, company_id, this_period
            )

            if chart_info_obj:
                chart_info_obj.status_amount_information = status_amount_information
                chart_info_obj.stage_amount_information = stage_amount_information
                chart_info_obj.save(update_fields=['status_amount_information', 'stage_amount_information'])
            else:
                LeadChartInformation.objects.create(
                    tenant_id=tenant_id, company_id=company_id, period_mapped=this_period,
                    status_amount_information=status_amount_information,
                    stage_amount_information=stage_amount_information
                )
            return True
        raise ValueError('This period not found. Can not update Lead chart information.')


class LeadHint(SimpleAbstractModel):
    opportunity = models.ForeignKey(
        'opportunity.Opportunity', on_delete=models.CASCADE, null=True, related_name='lead_opp_hint'
    )
    customer = models.ForeignKey(
        'saledata.Account', on_delete=models.CASCADE, null=True, related_name='lead_customer_hint'
    )
    customer_mobile = models.CharField(max_length=100, null=True)
    customer_email = models.CharField(max_length=150, null=True)

    class Meta:
        verbose_name = 'Lead Hint'
        verbose_name_plural = 'Lead Hints'
        ordering = ()
        default_permissions = ()
        permissions = ()

    @classmethod
    def check_and_create_lead_hint(cls, opportunity_obj, customer_mobile, customer_email, customer_id):
        if opportunity_obj:
            cls.objects.filter(opportunity=opportunity_obj).delete()
            cls.objects.create(
                opportunity_id=opportunity_obj.id,
                customer_mobile=customer_mobile,
                customer_email=customer_email,
                customer_id=customer_id
            )
        else:
            cls.objects.filter(customer_id=customer_id).update(
                customer_mobile=customer_mobile,
                customer_email=customer_email
            )
        return True


class LeadOpportunity(DataAbstractModel):
    lead = models.ForeignKey('lead.Lead', on_delete=models.CASCADE)
    opportunity = models.ForeignKey('opportunity.Opportunity', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Leads Opportunity'
        verbose_name_plural = 'Lead Opportunity'
        ordering = ()
        default_permissions = ()
        permissions = ()
