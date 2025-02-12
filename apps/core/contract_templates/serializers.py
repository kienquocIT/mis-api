from rest_framework import serializers

from apps.core.contract_templates.models import ContractTemplate
from .msg import ContractMsg
from apps.core.process.msg import ProcessMsg


class ContractTemplateListSerializers(serializers.ModelSerializer):
    employee_created = serializers.SerializerMethodField()
    application = serializers.SerializerMethodField()

    class Meta:
        model = ContractTemplate
        fields = (
            'id',
            'title',
            'application',
            'employee_created',
            'date_created',
        )

    @classmethod
    def get_employee_created(cls, obj):
        if obj.employee_created and hasattr(obj.employee_created, 'get_detail_minimal'):
            return obj.employee_created.get_detail_minimal()
        return {}

    @classmethod
    def get_application(cls, obj):
        return {
            'id': str(obj.application.id),
            'title': obj.application.title,
            'code': obj.application.code
        } if obj.application else {}


class ContractTemplateCreateSerializers(serializers.ModelSerializer):

    class Meta:
        model = ContractTemplate
        fields = (
            'title',
            'template',
            'application',
            'extra_data'
        )

    @classmethod
    def validate_application(cls, value):
        if not value:
            raise serializers.ValidationError({'detail': ProcessMsg.APPLICATION_NOT_FOUND})
        return value

    @classmethod
    def validate_extra_data(cls, value):
        if type(value) is dict:
            return value
        raise serializers.ValidationError({'detail': ContractMsg.ERROR_FIELD_DATA})

    def create(self, validated_data):
        info = ContractTemplate.objects.create(**validated_data)
        return info


class ContractTemplateDetailSerializers(serializers.ModelSerializer):
    application = serializers.SerializerMethodField()

    @classmethod
    def get_application(cls, obj):
        return {
            'id': str(obj.application.id),
            'title': obj.application.title,
            'code': obj.application.code
        } if obj.application else {}

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance

    class Meta:
        model = ContractTemplate
        fields = (
            'id',
            'title',
            'template',
            'application',
            'extra_data'
        )


class ContractTemplateDDListSerializers(serializers.ModelSerializer):

    class Meta:
        model = ContractTemplate
        fields = (
            'title',
            'template',
            'extra_data',
        )
