from rest_framework import serializers
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
            'current_lead_stage'
        )

    def validate(self, validate_data):
        return validate_data

    def create(self, validated_data):
        current_stage = LeadStage.objects.filter(
            tenant_id=validated_data['tenant_id'], company_id=validated_data['company_id'], level=1
        ).first()
        number = Lead.objects.filter(
            tenant_id=validated_data['tenant_id'], company_id=validated_data['company_id']
        ).count() + 1
        lead = Lead.objects.create(**validated_data, code=f'L000{number}', current_lead_stage=current_stage)

        # create notes
        for note_content in self.initial_data.get('note_data'):
            LeadNote.objects.create(lead=lead, note=note_content)

        # create config
        if 'assign_to_sale' in validated_data:
            LeadConfig.objects.create(lead=lead, assign_to_sale_config=validated_data['assign_to_sale'])

        return lead


class LeadDetailSerializer(serializers.ModelSerializer):
    industry = serializers.SerializerMethodField()
    assign_to_sale = serializers.SerializerMethodField()
    note_data = serializers.SerializerMethodField()
    config_data = serializers.SerializerMethodField()

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
        return [{
            'create_contact': config.create_contact,
            'convert_opp': config.convert_opp,
            'convert_opp_create': config.convert_opp_create,
            'convert_opp_select': config.convert_opp_select,
            'opp_select': config.opp_select,
            'convert_account_create': config.convert_account_create,
            'convert_account_select': config.convert_account_select,
            'account_select': config.account_select,
            'assign_to_sale_config': config.assign_to_sale_config
        } for config in obj.lead_configs.all()]


class LeadUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = '__all__'

    def validate(self, validate_data):
        return validate_data

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance
