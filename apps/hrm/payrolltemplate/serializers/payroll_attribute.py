from rest_framework import serializers

from apps.hrm.payrolltemplate.models import AttributeComponent
from apps.shared.translations.hrm import HRMMsg


class PayrollComponentListSerializers(serializers.ModelSerializer):

    class Meta:
        model = AttributeComponent
        fields = (
            'id',
            'component_title',
            'component_name',
            'component_code',
            'component_type',
            'component_formula',
            'component_mandatory'
        )


class PayrollComponentCreateSerializers(serializers.ModelSerializer):

    class Meta:
        model = AttributeComponent
        fields = (
            'component_title',
            'component_name',
            'component_code',
            'component_type',
            'component_formula',
            'component_mandatory'
        )


class PayrollComponentDetailSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        payroll_component_obj = AttributeComponent.objects.create(**validated_data)
        return payroll_component_obj

    class Meta:
        model = AttributeComponent
        fields = (
            'id',
            'component_title',
            'component_name',
            'component_code',
            'component_type',
            'component_formula',
            'component_mandatory',
        )


class PayrollComponentUpdateSerializer(serializers.ModelSerializer):
    component_code = serializers.CharField()

    def validated_component_code(self, attrs):
        if AttributeComponent.objects.filter(component_code=attrs).exclude(pk=self.instance.component_code).exists():
            raise serializers.ValidationError({'component_code': HRMMsg.PAYROLL_ATTR_ERROR_CODE})
        return attrs

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    class Meta:
        model = AttributeComponent
        fields = (
            'component_title',
            'component_name',
            'component_code',
            'component_type',
            'component_formula',
            'component_mandatory'
        )
