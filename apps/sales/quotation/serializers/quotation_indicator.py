from rest_framework import serializers

from apps.sales.quotation.models import QuotationIndicatorConfig
from apps.shared import SaleMsg
from apps.shared.extends.signals import ConfigDefaultData


class IndicatorListSerializer(serializers.ModelSerializer):
    formula_data = serializers.JSONField()
    formula_data_show = serializers.JSONField()

    class Meta:
        model = QuotationIndicatorConfig
        fields = (
            'id',
            'title',
            'code',
            'remark',
            'example',
            'order',
            'formula_data',
            'formula_data_show',
        )


class IndicatorDetailSerializer(serializers.ModelSerializer):
    formula_data = serializers.JSONField()
    formula_data_show = serializers.JSONField()

    class Meta:
        model = QuotationIndicatorConfig
        fields = (
            'id',
            'title',
            'code',
            'remark',
            'example',
            'order',
            'formula_data',
            'formula_data_show',
        )


class IndicatorCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = QuotationIndicatorConfig
        fields = (
            'title',
            'remark',
            'example',
            'order',
            'application_code'
        )

    def create(self, validated_data):
        indicator = QuotationIndicatorConfig.objects.create(**validated_data)
        return indicator


class IndicatorUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = QuotationIndicatorConfig
        fields = (
            'title',
            'remark',
            'example',
            'formula_data',
            'formula_data_show',
            'order',
        )

    @classmethod
    def validate_order(cls, value):
        if isinstance(value, int):
            if value > QuotationIndicatorConfig.objects.filter_current(fill__company=True).count() or value == 0:
                raise serializers.ValidationError({'detail': SaleMsg.INDICATOR_ORDER_OUT_OF_RANGE})
        return value

    @classmethod
    def update_other_indicator_if_change_order(cls, instance, validated_data):
        # change order to lower order => update order of records after instance += 1
        if validated_data['order'] < instance.order:
            other_indicators = QuotationIndicatorConfig.objects.filter_current(
                fill__company=True,
                order__gte=validated_data['order'],
                order__lte=instance.order,
            ).exclude(id=instance.id)
            for other_indicator in other_indicators:
                other_indicator.order = other_indicator.order + 1
                other_indicator.save(update_fields=['order'])
        # change order to higher order => update order of records after instance -= 1
        elif validated_data['order'] > instance.order:
            other_indicators = QuotationIndicatorConfig.objects.filter_current(
                fill__company=True,
                order__lte=validated_data['order'],
                order__gte=instance.order,
            ).exclude(id=instance.id)
            for other_indicator in other_indicators:
                other_indicator.order = other_indicator.order - 1
                other_indicator.save(update_fields=['order'])
        return True

    def update(self, instance, validated_data):
        # update other indicators if change order
        if 'order' in validated_data:
            self.update_other_indicator_if_change_order(instance=instance, validated_data=validated_data)
        # update
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        return instance


class IndicatorCompanyRestoreSerializer(serializers.ModelSerializer):

    class Meta:
        model = QuotationIndicatorConfig
        fields = ('title',)

    @staticmethod
    def restore_company_indicator(company_obj):
        QuotationIndicatorConfig.objects.filter(company_id=company_obj.id).delete()
        ConfigDefaultData(company_obj).quotation_indicator_config()
        return True

    def update(self, instance, validated_data):
        self.restore_company_indicator(company_obj=instance.company)
        return instance
