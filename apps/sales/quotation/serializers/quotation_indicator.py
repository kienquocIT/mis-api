from rest_framework import serializers

from apps.sales.quotation.models import Indicator


class IndicatorListSerializer(serializers.ModelSerializer):
    formula_data = serializers.JSONField()
    formula_data_show = serializers.JSONField()

    class Meta:
        model = Indicator
        fields = (
            'id',
            'title',
            'description',
            'order',
            'formula_data',
            'formula_data_show',
        )


class IndicatorDetailSerializer(serializers.ModelSerializer):
    formula_data = serializers.JSONField()
    formula_data_show = serializers.JSONField()

    class Meta:
        model = Indicator
        fields = (
            'id',
            'title',
            'description',
            'order',
            'formula_data',
            'formula_data_show',
        )


# Quotation
class IndicatorCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Indicator
        fields = (
            'title',
            'description',
            'order',
            'application_code'
        )

    def create(self, validated_data):
        indicator = Indicator.objects.create(**validated_data)
        return indicator


class IndicatorUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Indicator
        fields = (
            'title',
            'description',
            'formula_data',
            'formula_data_show',
        )

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance
