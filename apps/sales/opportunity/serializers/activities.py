from rest_framework import serializers
from apps.sales.opportunity.models import OpportunityCallLog
from apps.shared.translations.opportunity import OpportunityMsg


class OpportunityCallLogListSerializer(serializers.ModelSerializer):
    opportunity = serializers.SerializerMethodField()
    customer = serializers.SerializerMethodField()
    contact = serializers.SerializerMethodField()

    class Meta:
        model = OpportunityCallLog
        fields = (
            'id',
            'subject',
            'opportunity',
            'customer',
            'contact',
            'call_date',
            'input_result',
            'repeat'
        )

    @classmethod
    def get_opportunity(cls, obj):
        if obj.opportunity:
            return {
                'id': obj.opportunity_id,
                'code': obj.opportunity.code,
                'title': obj.opportunity.title
            }
        return {}

    @classmethod
    def get_customer(cls, obj):
        if obj.customer:
            return {
                'id': obj.customer_id,
                'code': obj.customer.code,
                'title': obj.customer.name
            }
        return {}

    @classmethod
    def get_contact(cls, obj):
        if obj.contact:
            return {
                'id': obj.contact_id,
                'fullname': obj.contact.fullname
            }
        return {}


class OpportunityCallLogCreateSerializer(serializers.ModelSerializer):
    input_result = serializers.CharField(required=True)

    class Meta:
        model = OpportunityCallLog
        fields = (
            'subject',
            'opportunity',
            'customer',
            'contact',
            'call_date',
            'input_result',
            'repeat'
        )

    @classmethod
    def validate_input_result(cls, value):
        if value:
            return value
        else:
            raise serializers.ValidationError({'detail': OpportunityMsg.ACTIVITIES_CALL_LOG_RESULT_NOT_NULL})


class OpportunityCallLogDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpportunityCallLog
        fields = (
            'id',
            'subject',
            'opportunity',
            'customer',
            'contact',
            'call_date',
            'input_result',
            'repeat'
        )
