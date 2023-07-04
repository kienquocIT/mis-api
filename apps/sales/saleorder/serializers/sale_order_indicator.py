from rest_framework import serializers

from apps.sales.saleorder.models import SaleOrderIndicatorConfig
from apps.shared.extends.signals import ConfigDefaultData


class SaleOrderIndicatorListSerializer(serializers.ModelSerializer):
    formula_data = serializers.JSONField()
    formula_data_show = serializers.JSONField()

    class Meta:
        model = SaleOrderIndicatorConfig
        fields = (
            'id',
            'title',
            'remark',
            'example',
            'order',
            'formula_data',
            'formula_data_show',
        )


class SaleOrderIndicatorDetailSerializer(serializers.ModelSerializer):
    formula_data = serializers.JSONField()
    formula_data_show = serializers.JSONField()

    class Meta:
        model = SaleOrderIndicatorConfig
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
class SaleOrderIndicatorCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = SaleOrderIndicatorConfig
        fields = (
            'title',
            'remark',
            'example',
            'order',
            'application_code'
        )

    def create(self, validated_data):
        indicator = SaleOrderIndicatorConfig.objects.create(**validated_data)
        return indicator


class SaleOrderIndicatorUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = SaleOrderIndicatorConfig
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


class SaleOrderIndicatorCompanyRestoreSerializer(serializers.ModelSerializer):

    class Meta:
        model = SaleOrderIndicatorConfig
        fields = ('title',)

    @staticmethod
    def restore_company_indicator(company_obj):
        SaleOrderIndicatorConfig.objects.filter(company_id=company_obj.id).delete()
        ConfigDefaultData(company_obj).quotation_indicator_config()
        return True

    def update(self, instance, validated_data):
        self.restore_company_indicator(company_obj=instance.company)
        return instance
