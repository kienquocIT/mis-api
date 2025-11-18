from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from apps.core.workflow.tasks import decorator_run_workflow
from apps.shared import AbstractCreateSerializerModel, BaseMsg, DisperseModel, AbstractDetailSerializerModel, \
    AbstractListSerializerModel
from apps.shared.translations.hrm import HRMMsg
from ..models import PayrollTemplate, SalaryTemplateEmployeeGroup

class AttributeListSerializers(serializers.Serializer):  # noqa
    name = serializers.CharField()
    code = serializers.CharField()
    type = serializers.IntegerField()
    source = serializers.IntegerField()
    formula_type = serializers.BooleanField(default=False)
    formula = serializers.JSONField(required=False, allow_null=True)
    data_source_component_data = serializers.JSONField(required=False, allow_null=True)
    mandatory = serializers.BooleanField()
    order = serializers.IntegerField()


class PayrollTemplateListSerializers(AbstractListSerializerModel):
    employee_created = serializers.SerializerMethodField()
    employee_inherit = serializers.SerializerMethodField()

    @classmethod
    def get_employee_created(cls, attrs):
        return {
            'id': str(attrs.employee_created.id), 'full_name': attrs.employee_created.get_full_name()
        } if attrs.employee_created else {}

    @classmethod
    def get_employee_inherit(cls, attrs):
        return {
            'id': str(attrs.employee_inherit.id), 'full_name': attrs.employee_inherit.get_full_name()
        } if attrs.employee_inherit else {}

    class Meta:
        model = PayrollTemplate
        fields = (
            'id',
            'title',
            'code',
            'remarks',
            'department_applied_data',
            'employee_inherit',
            'employee_created',
            'date_created',
        )


class PayrollTemplateCreateSerializers(AbstractCreateSerializerModel):
    attribute_list = AttributeListSerializers(many=True, allow_null=True, default=[])
    department_applied = serializers.ListSerializer(child=serializers.UUIDField())
    department_applied_data = serializers.JSONField(required=False, allow_null=True)

    @classmethod
    def validate_attribute_list(cls, value):
        if not len(value) > 0:
            raise serializers.ValidationError({'detail': HRMMsg.PAYROLL_TEMPLATE + BaseMsg.DOES_NOT_EXIST})
        return value

    @classmethod
    def validate_department_applied(cls, value):
        if value:
            group_models = DisperseModel(app_model='hr.group').get_model()
            list_group = group_models.objects.filter(id__in=value)
            if list_group.count() != len(value):
                raise serializers.ValidationError({'detail': _('Some Group') + BaseMsg.DOES_NOT_EXIST})
        return value

    @decorator_run_workflow
    def create(self, validated_data):
        employee_group = validated_data.pop('department_applied', None)
        template = PayrollTemplate.objects.create(**validated_data)
        if employee_group:
            group_mapped_list = []
            for group in employee_group:
                group_mapped_list.append(SalaryTemplateEmployeeGroup(
                    salary_template=template,
                    department_applied_id=group
                ))
            SalaryTemplateEmployeeGroup.objects.bulk_create(group_mapped_list)
        return template

    class Meta:
        model = PayrollTemplate
        fields = (
            'title',
            'department_applied',
            'department_applied_data',
            'remarks',
            'attribute_list',
        )


class PayrollTemplateDetailSerializers(AbstractDetailSerializerModel):
    employee_inherit = serializers.SerializerMethodField()

    @classmethod
    def get_employee_inherit(cls, obj):
        return {
            "id": obj.employee_inherit_id,
            "full_name": obj.employee_inherit.get_full_name()
        } if obj.employee_inherit else {}

    class Meta:
        model = PayrollTemplate
        fields = (
            'id',
            'title',
            'code',
            'department_applied_data',
            'remarks',
            'employee_inherit',
            'attribute_list',
        )


class PayrollTemplateUpdateSerializers(AbstractCreateSerializerModel):
    attribute_list = AttributeListSerializers(many=True)
    department_applied = serializers.ListSerializer(child=serializers.UUIDField())
    department_applied_data = serializers.JSONField(required=False, allow_null=True)

    @classmethod
    def validate_attribute_list(cls, value):
        if not len(value) > 0:
            raise serializers.ValidationError({'detail': BaseMsg.DOES_NOT_EXIST})
        return value

    def validate(self, validate_data):
        department = validate_data.get('department_applied')
        if department:
            group_models = DisperseModel(app_model='hr.group').get_model()
            list_group = group_models.objects.filter(id__in=department)
            if len(department) != list_group.count():
                raise serializers.ValidationError({'detail': BaseMsg.DOES_NOT_EXIST})
        return validate_data

    @decorator_run_workflow
    def update(self, instance, validated_data):
        employee_group = validated_data.pop('department_applied', None)
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        if employee_group:
            SalaryTemplateEmployeeGroup.objects.filter(salary_template=instance).delete()
            group_mapped_list = []
            for group in employee_group:
                group_mapped_list.append(SalaryTemplateEmployeeGroup(
                    salary_template=instance,
                    department_applied_id=group
                ))
            SalaryTemplateEmployeeGroup.objects.bulk_create(group_mapped_list)
        return instance

    class Meta:
        model = PayrollTemplate
        fields = (
            'title',
            'department_applied',
            'department_applied_data',
            'remarks',
            'attribute_list',
        )
