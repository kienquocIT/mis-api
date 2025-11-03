from rest_framework import serializers

from apps.hrm.payrolltemplate.models import AttributeComponent


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
