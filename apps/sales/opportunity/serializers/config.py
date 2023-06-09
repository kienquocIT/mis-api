from rest_framework import serializers

from apps.sales.opportunity.models import OpportunityDecisionFactor


class OpportunityDecisionFactorListSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpportunityDecisionFactor
        fields = (
            'id',
            'title'
        )


class OpportunityDecisionFactorCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpportunityDecisionFactor
        fields = (
            'title',
        )


class OpportunityDecisionFactorDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpportunityDecisionFactor
        fields = (
            'id',
            'title'
        )
