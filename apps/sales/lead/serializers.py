from rest_framework import serializers
from apps.shared import AbstractDetailSerializerModel
from apps.core.workflow.tasks import decorator_run_workflow
from apps.sales.lead.models import Lead, LeadNote, LeadStage, LeadConfig, LEAD_SOURCE, LEAD_STATUS

__all__ = [
    'LeadListSerializer',
    'LeadCreateSerializer',
    'LeadDetailSerializer',
    'LeadUpdateSerializer'
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
            'account_name',
            'industry',
            'total_employees',
            'revenue',
            'source',
            'lead_status',
            'assign_to_sale',
            'system_status'
        )

    def validate(self, validate_data):
        return validate_data

    @decorator_run_workflow
    def create(self, validated_data):
        current_stage = LeadStage.objects.filter(
            tenant_id=validated_data['tenant_id'], company_id=validated_data['company_id'], level=1
        ).first()
        if current_stage:
            lead = Lead.objects.create(**validated_data, current_lead_stage=current_stage)

            # create notes
            for note_content in self.initial_data.get('note_data'):
                LeadNote.objects.create(lead=lead, note=note_content)

            # create config
            if 'assign_to_sale' in validated_data:
                LeadConfig.objects.create(lead=lead, assign_to_sale_config=validated_data['assign_to_sale'])

            return lead
        else:
            raise serializers.ValidationError({'Lead stage': "Lead stage not found"})


class LeadDetailSerializer(AbstractDetailSerializerModel):
    industry = serializers.SerializerMethodField()
    assign_to_sale = serializers.SerializerMethodField()
    note_data = serializers.SerializerMethodField()
    config_data = serializers.SerializerMethodField()
    current_lead_stage = serializers.SerializerMethodField()

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
            'account_name',
            'industry',
            'total_employees',
            'revenue',
            'source',
            'lead_status',
            'assign_to_sale',
            'current_lead_stage',
            'note_data',
            'config_data'
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
            'opp_select': config.opp_select_id,
            'convert_account_create': config.convert_account_create,
            'convert_account_select': config.convert_account_select,
            'account_select': config.account_select_id,
            'assign_to_sale_config': {
                'id': config.assign_to_sale_config_id,
                'code': config.assign_to_sale_config.code,
                'full_name': config.assign_to_sale_config.get_full_name(2),
            } if config.assign_to_sale_config else {},
            'contact_mapped': {
                'id': config.contact_mapped_id,
                'code': config.contact_mapped.code,
                'fullname': config.contact_mapped.fullname,
            } if config.contact_mapped else {}
        } if config else {}

    @classmethod
    def get_current_lead_stage(cls, obj):
        return {
            'title': obj.current_lead_stage.stage_title,
            'level': obj.current_lead_stage.level,
        }


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
            'account_name',
            'industry',
            'total_employees',
            'revenue',
            'source',
            'lead_status',
            'assign_to_sale',
            'system_status'
        )

    def validate(self, validate_data):
        return validate_data

    @decorator_run_workflow
    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        # update notes
        LeadNote.objects.filter(lead=instance).delete()
        for note_content in self.initial_data.get('note_data'):
            LeadNote.objects.create(lead=instance, note=note_content)

        # update config
        LeadConfig.objects.filter(lead=instance).delete()
        if 'assign_to_sale' in validated_data:
            LeadConfig.objects.create(lead=instance, assign_to_sale_config=validated_data['assign_to_sale'])

        return instance


class LeadStageListSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadStage
        fields = (
            'id',
            'stage_title',
            'level'
        )
