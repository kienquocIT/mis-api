from rest_framework import serializers
from apps.sales.opportunity.models import OpportunityCallLog, OpportunityEmail
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


class OpportunityEmailListSerializer(serializers.ModelSerializer):
    opportunity = serializers.SerializerMethodField()
    email_to_contact = serializers.SerializerMethodField()

    class Meta:
        model = OpportunityEmail
        fields = (
            'id',
            'subject',
            'email_to',
            'email_cc_list',
            'content',
            'date_created',
            'opportunity',
            'email_to_contact'
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
    def get_email_to_contact(cls, obj):
        if obj.email_to_contact:
            return {
                'id': obj.email_to_contact_id,
                'fullname': obj.email_to_contact.fullname,
                'email': obj.email_to_contact.email
            }
        return {}


class OpportunityEmailCreateSerializer(serializers.ModelSerializer):
    content = serializers.CharField(required=True)

    class Meta:
        model = OpportunityEmail
        fields = (
            'subject',
            'email_to',
            'email_cc_list',
            'content',
            'opportunity',
            'email_to_contact'
        )

    @classmethod
    def validate_email_to(cls, value):
        if len(value.split(' ')) > 1 or not value.endswith("@gmail.com"):
            raise serializers.ValidationError({'To': OpportunityMsg.EMAIL_TO_NOT_VALID})
        return value

    @classmethod
    def validate_email_cc_list(cls, value):
        for item in value:
            if len(item.split(' ')) > 1 or not item.endswith("@gmail.com"):
                raise serializers.ValidationError({'Cc': OpportunityMsg.EMAIL_CC_NOT_VALID})
        return value


class OpportunityEmailDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpportunityEmail
        fields = (
            'id',
            'subject',
            'email_to',
            'email_cc_list',
            'content',
            'date_created',
            'opportunity',
            'email_to_contact'
        )
