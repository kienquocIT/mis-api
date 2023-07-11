from rest_framework import serializers

from apps.sales.opportunity.models import CustomerDecisionFactor, OpportunityConfig, OpportunityConfigStage, \
    StageCondition


class OpportunityConfigDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpportunityConfig
        fields = (
            'id',
            'is_select_stage',
            'is_input_win_rate',
            'is_account_manager_create',
        )


class OpportunityConfigUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpportunityConfig
        fields = (
            'is_select_stage',
            'is_input_win_rate',
            'is_account_manager_create',
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


class OpportunityConfigStageListSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpportunityConfigStage
        fields = '__all__'


class OpportunityConfigStageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpportunityConfigStage
        fields = (
            'indicator',
            'description',
            'win_rate',
        )


class OpportunityConfigStageDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpportunityConfigStage
        fields = '__all__'


class OpportunityConfigStageUpdateSerializer(serializers.ModelSerializer):
    condition_datas = serializers.ListField(required=False)
    win_rate = serializers.FloatField(required=False)

    class Meta:
        model = OpportunityConfigStage
        fields = (
            'condition_datas',
            'win_rate',
        )

    @classmethod
    def common_update_stage_condition(cls, instance, data):
        StageCondition.objects.filter(stage=instance).delete()
        bulk_data = []
        for item in data:
            stage_condition = StageCondition(
                stage=instance,
                condition_property_id=item['condition_property']['id'],
                comparison_operator=item['comparison_operator'],
                compare_data=item['compare_data']
            )
            bulk_data.append(stage_condition)
        StageCondition.objects.bulk_create(bulk_data)
        return True

    def update(self, instance, validated_data):
        if 'condition_datas' in validated_data:
            self.common_update_stage_condition(instance, validated_data['condition_datas'])
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance
