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
        LeadConfig.objects.create(lead=lead, **self.initial_data.get('config_data'))

        return lead


class LeadDetailSerializer(serializers.ModelSerializer):
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
            'current_lead_stage'
        )


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
