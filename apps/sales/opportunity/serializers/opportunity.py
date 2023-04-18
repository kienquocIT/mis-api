from rest_framework import serializers

from apps.sale.saledata.models.accounts import Account
from apps.sales.opportunity.models.opportunity import Opportunity
from apps.shared import AccountsMsg


class OpportunityListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Opportunity
        fields = (
            'id',
            'title',
            'code'
        )


class OpportunityCreateSerializer(serializers.ModelSerializer):
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
