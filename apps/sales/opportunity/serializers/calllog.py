from rest_framework import serializers
from apps.core.hr.models import Employee
from apps.masterdata.saledata.models import Product, ProductCategory, UnitOfMeasure, Tax, Contact
from apps.masterdata.saledata.models import Account
from apps.sales.opportunity.models import OpportunityCallLog
from apps.shared import AccountsMsg, HRMsg
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
            'result',
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
    class Meta:
        model = OpportunityCallLog
        fields = (
            'subject',
            'opportunity',
            'customer',
            'contact',
            'call_date',
            'result',
            'repeat'
        )


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
            'result',
            'repeat'
        )
