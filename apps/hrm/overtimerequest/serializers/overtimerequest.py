from rest_framework import serializers

from apps.core.workflow.tasks import decorator_run_workflow
from apps.hrm.overtimerequest.models import OvertimeRequest
from apps.shared import AbstractCreateSerializerModel, AbstractDetailSerializerModel, DisperseModel


class OvertimeRequestListSerializers(serializers.ModelSerializer):
    class Meta:
        model = OvertimeRequest
        fields = (
            'id',
            'title',
            'code',
            'employee_created_data',
            'employee_list_data',
            'employee_inherit_data',
            'ot_type',
            'date_created',
            'system_status',
        )


class OvertimeRequestCreateSerializers(AbstractCreateSerializerModel):

    def validate(self, validate_data):
        if len(validate_data['employee_list']):
            employee_list = DisperseModel(app_model='hr.Employee').get_model().objects.filter(
                id__in=validate_data['employee_list'],
            )
            if employee_list.exists() and employee_list.count() == len(validate_data['employee_list']):
                validate_data['employee_list_data'] = [{
                    'id': str(item.id),
                    'code': item.code,
                    'group': {'id': str(item.group.id), 'title': item.group.title} if item.group else {},
                    'full_name': item.get_full_name()
                } for item in employee_list]
        return validate_data

    @decorator_run_workflow
    def create(self, validated_data):
        overtime = OvertimeRequest.objects.create(**validated_data)
        return overtime

    class Meta:
        model = OvertimeRequest
        fields = (
            'title',
            'employee_inherit',
            'employee_list',
            'employee_list_data',
            'ot_type',
            'start_date',
            'end_date',
            'start_time',
            'end_time',
            'reason',
            'shift',
        )


class OvertimeRequestDetailSerializers(AbstractDetailSerializerModel):
    shift = serializers.SerializerMethodField()

    @classmethod
    def get_shift(cls, obj):
        item_list = {
            'id': obj.shift.id,
            'code': obj.shift.code,
            'title': obj.shift.title,
            'checkin_time': obj.shift.checkin_time,
            'checkout_time': obj.shift.checkout_time,
        } if obj.shift else {}
        return item_list

    class Meta:
        model = OvertimeRequest
        fields = (
            'id',
            'title',
            'code',
            'employee_inherit_data',
            'employee_list_data',
            'employee_created_data',
            'ot_type',
            'start_date',
            'end_date',
            'start_time',
            'end_time',
            'reason',
            'shift',
        )


class OvertimeRequestUpdateSerializers(AbstractCreateSerializerModel):
    employee_list = serializers.JSONField(required=False, allow_null=True)

    def validate(self, validate_data):
        if len(validate_data['employee_list']):
            employee_list = DisperseModel(app_model='hr.Employee').get_model().objects.filter(
                id__in=validate_data['employee_list'],
            )
            if employee_list.exists() and employee_list.count() == len(validate_data['employee_list']):
                validate_data['employee_list_data'] = [{
                    'id': str(item.id),
                    'code': item.code,
                    'group': {'id': str(item.group.id), 'title': item.group.title} if item.group else {},
                    'full_name': item.get_full_name()
                } for item in employee_list]
        return validate_data

    @decorator_run_workflow
    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance

    class Meta:
        model = OvertimeRequest
        fields = (
            'title',
            'employee_inherit',
            'employee_list',
            'employee_list_data',
            'ot_type',
            'start_date',
            'end_date',
            'start_time',
            'end_time',
            'reason',
            'shift',
        )
