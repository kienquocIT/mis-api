from rest_framework import serializers

from apps.sales.quotation.models import QuotationIndicatorConfig
from apps.shared.extends.signals import ConfigDefaultData


class IndicatorListSerializer(serializers.ModelSerializer):
    formula_data = serializers.JSONField()
    formula_data_show = serializers.JSONField()

    class Meta:
        model = QuotationIndicatorConfig
        fields = (
            'id',
            'title',
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
            'remark',
            'example',
            'order',
            'formula_data',
            'formula_data_show',
        )


# Quotation
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
        )

    def update(self, instance, validated_data):
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
