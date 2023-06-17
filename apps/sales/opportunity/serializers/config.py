from rest_framework import serializers

from apps.sales.opportunity.models import CustomerDecisionFactor, OpportunityConfig


class OpportunityConfigDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpportunityConfig
        fields = (
            'id',
            'is_select_stage',
            'is_input_win_rate',
        )


class OpportunityConfigUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpportunityConfig
        fields = (
            'is_select_stage',
            'is_input_win_rate',
        )


class CustomerDecisionFactorListSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomerDecisionFactor
        fields = (
            'id',
            'title',
            'company_id'
        )


class CustomerDecisionFactorCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomerDecisionFactor
        fields = (
            'title',
        )


class CustomerDecisionFactorDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerDecisionFactor
        fields = (
            'id',
            'title'
        )
