from rest_framework import serializers

from apps.core.contract_templates.models import ContractTemplate
from apps.core.process.msg import ProcessMsg
from apps.shared import DisperseModel, ContractTemplateMsg


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
            'members',
            'signatures'
        )

    @classmethod
    def validate_application(cls, value):
        if not value:
            raise serializers.ValidationError({'detail': ProcessMsg.APPLICATION_NOT_FOUND})
        return value

    @classmethod
    def validate_members(cls, attrs):
        if len(attrs) > 0:
            objs = DisperseModel(app_model='hr.Employee').get_model().objects.filter_current(
                fill__tenant=True, fill__company=True, id__in=attrs
            )
            if objs.count() != len(attrs):
                raise serializers.ValidationError({'members': ContractTemplateMsg.MEMBER_NOT_EXIST})
        return attrs

    def create(self, validated_data):
        info = ContractTemplate.objects.create(**validated_data)
        return info


class ContractTemplateDetailSerializers(serializers.ModelSerializer):
    application = serializers.SerializerMethodField()

    class Meta:
        model = ContractTemplate
        fields = (
            'id',
            'title',
            'template',
            'application',
            'members',
            'signatures'
        )

    @classmethod
    def get_application(cls, obj):
        return {
            'id': str(obj.application.id),
            'title': obj.application.title,
            'code': obj.application.code
        } if obj.application else {}
