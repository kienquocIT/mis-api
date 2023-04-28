from rest_framework import serializers

from apps.sale.saledata.models.accounts import Account
from apps.sales.opportunity.models import Opportunity
from apps.shared import AccountsMsg


class OpportunityListSerializer(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField()

    class Meta:
        model = Opportunity
        fields = (
            'id',
            'title',
            'code',
            'customer'
        )

    @classmethod
    def get_customer(cls, obj):
        if obj.customer:
            return {
                'id': obj.customer_id,
                'title': obj.customer.name,
                'code': obj.customer.code
            }
        return {}


class OpportunityCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField()
    customer = serializers.UUIDField()

    class Meta:
        model = Opportunity
        fields = (
            'title',
            'customer'
        )

    @classmethod
    def validate_customer(cls, value):
        try:
            return Account.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
        except Account.DoesNotExist:
            raise serializers.ValidationError({'detail': AccountsMsg.ACCOUNT_NOT_EXIST})

    def create(self, validated_data):
        opportunity = Opportunity.objects.create(**validated_data)
        return opportunity


class OpportunityUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Opportunity
        fields = (
            'title',
            'code',
            'customer'
        )

    @classmethod
    def validate_customer(cls, value):
        try:
            return Account.objects.get_current(
                fill__tenant=True,
                fill__company=True,
                id=value
            )
        except Account.DoesNotExist:
            raise serializers.ValidationError({'detail': AccountsMsg.ACCOUNT_NOT_EXIST})

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance
