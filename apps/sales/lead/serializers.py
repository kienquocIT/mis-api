from rest_framework import serializers
from django.utils import timezone
from apps.masterdata.saledata.models import Periods
from apps.sales.lead.models import (
    Lead, LeadNote, LeadStage, LeadConfig, LEAD_SOURCE, LEAD_STATUS,
    LeadChartInformation, LeadHint
)

__all__ = [
    'LeadListSerializer',
    'LeadCreateSerializer',
    'LeadDetailSerializer',
    'LeadUpdateSerializer',
    'LeadStageListSerializer'
]


class LeadListSerializer(serializers.ModelSerializer):
    source = serializers.SerializerMethodField()
    lead_status = serializers.SerializerMethodField()

    class Meta:
        model = Lead
        fields = (
            'id',
            'code',
            'title',
            'contact_name',
            'source',
            'lead_status',
            'date_created'
        )

    @classmethod
    def get_source(cls, obj):
        return str(dict(LEAD_SOURCE).get(obj.source))

    @classmethod
    def get_lead_status(cls, obj):
        return str(dict(LEAD_STATUS).get(obj.lead_status))


class LeadCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = (
            'title',
            'contact_name',
            'job_title',
            'mobile',
            'email',
            'company_name',
            'industry',
            'total_employees',
            'revenue',
            'source',
            'lead_status',
            'assign_to_sale',
        )

    def validate(self, validate_data):
        return validate_data

    def create(self, validated_data):
        number = Lead.objects.filter(
            tenant_id=validated_data['tenant_id'], company_id=validated_data['company_id'], is_delete=False
        ).count() + 1
        code = f'L000{number}'
        current_stage = LeadStage.objects.filter(
            tenant_id=validated_data['tenant_id'], company_id=validated_data['company_id'], level=1
        ).first()
        this_period = Periods.objects.filter(
            tenant_id=validated_data['tenant_id'], company_id=validated_data['company_id'],
            fiscal_year=timezone.now().year
        ).first()
        if current_stage and this_period:
            lead = Lead.objects.create(
                **validated_data, current_lead_stage=current_stage, code=code, system_status=1,
                period_mapped=this_period
            )

            # create notes
            for note_content in self.initial_data.get('note_data', []):
                LeadNote.objects.create(lead=lead, note=note_content)

            # create config
            if 'assign_to_sale' in validated_data:
                LeadConfig.objects.create(lead=lead, assign_to_sale_config=validated_data['assign_to_sale'])

            return lead
        raise serializers.ValidationError({'Lead stage': "Lead stage not found"})


class LeadDetailSerializer(serializers.ModelSerializer):
    industry = serializers.SerializerMethodField()
    assign_to_sale = serializers.SerializerMethodField()
    note_data = serializers.SerializerMethodField()
    config_data = serializers.SerializerMethodField()
    current_lead_stage = serializers.SerializerMethodField()
    related_opps = serializers.SerializerMethodField()
    related_leads = serializers.SerializerMethodField()

    class Meta:
        model = Lead
        fields = (
            'id',
            'code',
            'title',
            'contact_name',
            'job_title',
            'mobile',
            'email',
            'company_name',
            'industry',
            'total_employees',
            'revenue',
            'source',
            'lead_status',
            'assign_to_sale',
            'current_lead_stage',
            'note_data',
            'config_data',
            'related_opps',
            'related_leads'
        )

    @classmethod
    def get_industry(cls, obj):
        return {
            'id': obj.industry_id,
            'code': obj.industry.code,
            'title': obj.industry.title
        } if obj.industry else {}

    @classmethod
    def get_assign_to_sale(cls, obj):
        return {
            'id': obj.assign_to_sale_id,
            'code': obj.assign_to_sale.code,
            'full_name': obj.assign_to_sale.get_full_name(2)
        } if obj.assign_to_sale else {}

    @classmethod
    def get_note_data(cls, obj):
        return [note_content.note for note_content in obj.lead_notes.all()]

    @classmethod
    def get_config_data(cls, obj):
        config = obj.lead_configs.first()
        return {
            'create_contact': config.create_contact,
            'convert_opp': config.convert_opp,
            'convert_opp_create': config.convert_opp_create,
            'convert_opp_select': config.convert_opp_select,
            'account_mapped': {
                'id': config.account_mapped_id,
                'code': config.account_mapped.code,
                'name': config.account_mapped.name,
            } if config.account_mapped else None,
            'assign_to_sale_config': {
                'id': config.assign_to_sale_config_id,
                'code': config.assign_to_sale_config.code,
                'full_name': config.assign_to_sale_config.get_full_name(2),
            } if config.assign_to_sale_config else {},
            'contact_mapped': {
                'id': config.contact_mapped_id,
                'code': config.contact_mapped.code,
                'fullname': config.contact_mapped.fullname,
            } if config.contact_mapped else {},
            'opp_mapped': {
                'id': config.opp_mapped_id,
                'code': config.opp_mapped.code,
                'title': config.opp_mapped.title,
            } if config.opp_mapped else {}
        } if config else {}

    @classmethod
    def get_current_lead_stage(cls, obj):
        return {
            'title': obj.current_lead_stage.stage_title,
            'level': obj.current_lead_stage.level,
        }

    @classmethod
    def get_related_opps(cls, obj):
        related_opps = []
        config = obj.lead_configs.first()
        if config:
            if config.convert_opp:
                return []
        existed = []

        all_hint = LeadHint.objects.all()
        hints_by_mobile = all_hint.filter(customer_mobile=obj.mobile) if obj.mobile else []
        hints_by_email = all_hint.filter(customer_email=obj.email) if obj.email else []
        for hint in list(hints_by_mobile) + list(hints_by_email):
            if str(hint.id) not in existed:
                related_opps.append({
                    'id': str(hint.opportunity_id), 'code': hint.opportunity.code, 'title': hint.opportunity.title
                })
                existed.append(str(hint.opportunity_id))
        return related_opps

    @classmethod
    def get_related_leads(cls, obj):
        related_leads = []
        config = obj.lead_configs.first()
        if config:
            if config.convert_opp:
                return []
        all_lead = Lead.objects.filter(tenant=obj.tenant, company=obj.company)
        existed = []
        for lead in all_lead:
            filer_by_contact_name = all_lead.filter(contact_name__icontains=lead.contact_name).count()
            filer_by_mobile = all_lead.filter(mobile__icontains=lead.mobile).count()
            filer_by_email = all_lead.filter(email__icontains=lead.email).count()
            filer_by_company_name = all_lead.filter(company_name__icontains=lead.company_name).count()
            if sum([filer_by_contact_name, filer_by_mobile, filer_by_email, filer_by_company_name]) > 0:
                if str(lead.id) not in existed:
                    related_leads.append({
                        'id': lead.id, 'code': lead.code, 'title': lead.title
                    })
                    existed.append(str(lead.id))
        return related_leads


class LeadUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = (
            'title',
            'contact_name',
            'job_title',
            'mobile',
            'email',
            'company_name',
            'industry',
            'total_employees',
            'revenue',
            'source',
            'lead_status',
            'assign_to_sale',
        )

    def validate(self, validate_data):
        return validate_data

    @classmethod
    def goto_stage(cls, instance):
        stage_goto = LeadStage.objects.filter(
            company=instance.company, tenant=instance.tenant, level=3
        ).first()
        if instance.lead_status == 2 and stage_goto:
            instance.current_lead_stage = stage_goto
            instance.lead_status = 3
        else:
            raise serializers.ValidationError({
                'error': 'Can not go to this Stage. You have to go to "Marketing Qualified Lead" first.'
            })
        instance.save()
        return instance

    @classmethod
    def convert_opp(cls, instance, config, opp_mapped_id):
        if instance.current_lead_stage.level != 1:
            if config:
                config.convert_opp = True
                config.convert_opp_create = False
                config.convert_opp_select = True
                config.opp_mapped_id = opp_mapped_id
                config.save(update_fields=[
                    'convert_opp', 'convert_opp_create', 'convert_opp_select', 'opp_mapped_id'
                ])
                stage = LeadStage.objects.filter(
                    company=instance.company, tenant=instance.tenant, level=4
                ).first()
                if stage:
                    instance.current_lead_stage = stage
                    instance.lead_status = 4
        instance.save()
        return instance

    def update(self, instance, validated_data):
        this_period = Periods.objects.filter(
            tenant_id=instance.tenant_id, company_id=instance.company_id,
            fiscal_year=timezone.now().year
        ).first()
        config = instance.lead_configs.first()
        if str(this_period.id) == str(instance.period_mapped_id):
            if 'goto_stage' in self.context:
                self.goto_stage(instance)
            elif 'convert_opp' in self.context:
                self.convert_opp(instance, config, self.context.get('opp_mapped_id'))
            else:
                if config.contact_mapped or config.convert_opp:
                    raise serializers.ValidationError(
                        {'Finished': "Can not update this Lead. Contact or Opp has been created already."}
                    )
                for key, value in validated_data.items():
                    setattr(instance, key, value)
                instance.save()

                # update notes
                LeadNote.objects.filter(lead=instance).delete()
                for note_content in self.initial_data.get('note_data', []):
                    LeadNote.objects.create(lead=instance, note=note_content)

            return instance
        raise serializers.ValidationError({'Lead period': "Can not update lead of other period."})


class LeadStageListSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadStage
        fields = (
            'id',
            'stage_title',
            'level'
        )


class LeadChartListSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadChartInformation
        fields = (
            'id',
            'status_amount_information',
            'stage_amount_information',
            'period_mapped'
        )
